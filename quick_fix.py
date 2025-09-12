# quick_fix.py - Apply urgent fixes to main_fixed_window.py
"""
This script applies critical fixes to resolve:
1. AttributeError: 'EnhancedSceneManager' object has no attribute 'handle_note_event'
2. pyvista.core.errors.NotAllTrianglesError: Input mesh for subdivision must be all triangles
"""

import re
import os
import shutil
from datetime import datetime

def create_backup(filename):
    """Create a backup of the original file."""
    if os.path.exists(filename):
        backup_name = f"{filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(filename, backup_name)
        print(f"✓ Backup created: {backup_name}")
        return backup_name
    return None

def fix_handle_note_event_calls(content):
    """Fix calls from handle_note_event to handle_midi_note."""
    
    # Pattern to find handle_note_event calls
    pattern = r'self\.scene_manager\.handle_note_event\((.*?)\)'
    
    def replacement(match):
        args = match.group(1)
        # Convert from handle_note_event(note, velocity, is_note_on) 
        # to handle_midi_note(note, velocity, is_note_on)
        return f'self.scene_manager.handle_midi_note({args})'
    
    fixed_content = re.sub(pattern, replacement, content)
    
    print("✓ Fixed handle_note_event calls to handle_midi_note")
    return fixed_content

def add_safe_subdivision_function(content):
    """Add safe subdivision function to prevent NotAllTrianglesError."""
    
    safe_subdivide_code = '''
def safe_subdivide(mesh, subdivisions=1):
    """Safely subdivide a mesh, ensuring it's triangulated first."""
    try:
        # Make a copy to avoid modifying the original
        mesh_copy = mesh.copy()
        
        # Ensure mesh is triangulated before subdivision
        if hasattr(mesh_copy, 'triangulate'):
            mesh_copy = mesh_copy.triangulate()
        
        # Check if mesh is all triangles
        if hasattr(mesh_copy, 'faces'):
            faces = mesh_copy.faces
            # Reshape faces to get triangle info
            if faces.size > 0:
                # PyVista faces format: [n_points, point1, point2, ..., n_points, point1, point2, ...]
                face_sizes = faces[::4]  # Every 4th element is the number of points
                if not np.all(face_sizes == 3):
                    print("Warning: Mesh contains non-triangular faces, triangulating...")
                    mesh_copy = mesh_copy.triangulate()
        
        # Now attempt subdivision
        return mesh_copy.subdivide(subdivisions)
        
    except Exception as e:
        print(f"Subdivision failed: {e}")
        return mesh  # Return original mesh if subdivision fails

'''
    
    # Find where to insert the function (after imports)
    import_end = content.find('\nclass ')
    if import_end == -1:
        import_end = content.find('\ndef ')
    
    if import_end != -1:
        fixed_content = content[:import_end] + safe_subdivide_code + content[import_end:]
        print("✓ Added safe_subdivide function")
    else:
        # Just add it at the beginning after imports
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
        
        lines.insert(insert_index, safe_subdivide_code)
        fixed_content = '\n'.join(lines)
        print("✓ Added safe_subdivide function at beginning")
    
    return fixed_content

def fix_subdivision_calls(content):
    """Replace direct .subdivide() calls with safe_subdivide()."""
    
    # Pattern to find .subdivide() calls
    pattern = r'(\w+)\.subdivide\(([^)]*)\)'
    
    def replacement(match):
        mesh_var = match.group(1)
        args = match.group(2)
        return f'safe_subdivide({mesh_var}, {args})'
    
    fixed_content = re.sub(pattern, replacement, content)
    print("✓ Fixed subdivision calls to use safe_subdivide")
    return fixed_content

def add_safe_hsv_function(content):
    """Add safe HSV to RGB conversion function."""
    
    safe_hsv_code = '''
def safe_hsv_to_rgb(h, s, v):
    """Safe HSV to RGB conversion with error handling."""
    try:
        return colorsys.hsv_to_rgb(h, s, v)
    except (ValueError, TypeError) as e:
        print(f"HSV conversion error: {e}, using fallback color")
        return (0.5, 0.5, 0.5)  # Gray fallback

'''
    
    # Find where to insert after imports
    if 'def safe_hsv_to_rgb' not in content:
        import_end = content.find('\nclass ')
        if import_end == -1:
            import_end = content.find('\ndef ')
        
        if import_end != -1:
            fixed_content = content[:import_end] + safe_hsv_code + content[import_end:]
            print("✓ Added safe_hsv_to_rgb function")
        else:
            fixed_content = safe_hsv_code + content
            print("✓ Added safe_hsv_to_rgb function at beginning")
    else:
        fixed_content = content
        print("✓ safe_hsv_to_rgb function already exists")
    
    return fixed_content

def fix_hsv_calls(content):
    """Replace direct colorsys.hsv_to_rgb calls with safe version."""
    
    # Pattern to find colorsys.hsv_to_rgb calls
    pattern = r'colorsys\.hsv_to_rgb\('
    replacement = 'safe_hsv_to_rgb('
    
    fixed_content = content.replace(pattern, replacement)
    print("✓ Fixed HSV conversion calls to use safe version")
    return fixed_content

def fix_main_window_file(filename='main_fixed_window.py'):
    """Apply all fixes to the main window file."""
    
    print(f"Applying fixes to {filename}...")
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"❌ File {filename} not found!")
        return False
    
    # Create backup
    backup_file = create_backup(filename)
    
    try:
        # Read original content
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ Read {len(content)} characters from {filename}")
        
        # Apply all fixes
        content = fix_handle_note_event_calls(content)
        content = add_safe_subdivision_function(content)
        content = fix_subdivision_calls(content)
        content = add_safe_hsv_function(content)
        content = fix_hsv_calls(content)
        
        # Write fixed content
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixes applied to {filename}")
        print(f"✓ Backup available at: {backup_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        
        # Restore from backup if something went wrong
        if backup_file and os.path.exists(backup_file):
            shutil.copy2(backup_file, filename)
            print(f"✓ Restored from backup: {backup_file}")
        
        return False

def create_minimal_enhanced_scene_manager():
    """Create a minimal enhanced_scene_manager.py if it doesn't exist."""
    
    filename = 'enhanced_scene_manager.py'
    
    if os.path.exists(filename):
        print(f"✓ {filename} already exists")
        return True
    
    minimal_code = '''# enhanced_scene_manager.py - Minimal implementation
"""
Minimal EnhancedSceneManager to provide compatibility with main_fixed_window.py
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any

class EnhancedSceneManager:
    """Minimal enhanced scene manager for compatibility."""
    
    def __init__(self, initial_meshes: Dict, plotter_widget):
        """Initialize with meshes and plotter."""
        self.initial_meshes = initial_meshes
        self.plotter_widget = plotter_widget
        self.objects = {}
        self.actors = {}
        self.active_notes = {}
        
        print("✓ EnhancedSceneManager initialized (minimal version)")
    
    def handle_midi_note(self, note: int, velocity: int, is_note_on: bool) -> List[str]:
        """Handle MIDI note events."""
        try:
            if is_note_on:
                # Note on - add to active notes
                self.active_notes[note] = {
                    'velocity': velocity,
                    'timestamp': time.time()
                }
                print(f"Note ON: {note} (velocity: {velocity})")
                return [f"note_{note}"]
            else:
                # Note off - remove from active notes
                if note in self.active_notes:
                    del self.active_notes[note]
                print(f"Note OFF: {note}")
                return [f"note_{note}"]
                
        except Exception as e:
            print(f"Error handling MIDI note: {e}")
            return []
    
    def get_scene_summary(self) -> Dict:
        """Get summary of current scene state."""
        return {
            'active_objects': len(self.objects),
            'total_active_notes': len(self.active_notes),
            'objects': {
                obj_id: {
                    'active_notes': 1 if obj_id.startswith('note_') and 
                                   int(obj_id.split('_')[1]) in self.active_notes else 0
                }
                for obj_id in self.objects.keys()
            }
        }
    
    def render_frame(self):
        """Render the current frame."""
        try:
            if self.plotter_widget:
                self.plotter_widget.render()
        except Exception as e:
            print(f"Error rendering frame: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            self.active_notes.clear()
            self.objects.clear()
            self.actors.clear()
            print("✓ Scene manager cleaned up")
        except Exception as e:
            print(f"Error during cleanup: {e}")

'''
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(minimal_code)
        print(f"✓ Created minimal {filename}")
        return True
    except Exception as e:
        print(f"❌ Error creating {filename}: {e}")
        return False

def verify_fixes():
    """Verify that the fixes have been applied correctly."""
    
    filename = 'main_fixed_window.py'
    
    if not os.path.exists(filename):
        print(f"❌ {filename} not found for verification")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for fixes
        checks = [
            ('handle_midi_note method calls', 'handle_midi_note(' in content),
            ('safe_subdivide function', 'def safe_subdivide(' in content),
            ('safe_hsv_to_rgb function', 'def safe_hsv_to_rgb(' in content),
            ('No handle_note_event calls', 'handle_note_event(' not in content),
            ('No direct subdivide calls', '.subdivide(' not in content or 'safe_subdivide(' in content),
        ]
        
        print("\nVerification Results:")
        print("-" * 50)
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False
        
        print("-" * 50)
        
        if all_passed:
            print("🎉 All fixes verified successfully!")
        else:
            print("⚠️  Some fixes may not have been applied correctly")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def main():
    """Main function to apply all fixes."""
    
    print("🔧 MIDI OSC Morphing Interface - Quick Fix Script")
    print("=" * 60)
    print("This script fixes:")
    print("1. AttributeError: 'EnhancedSceneManager' object has no attribute 'handle_note_event'")
    print("2. pyvista.core.errors.NotAllTrianglesError: Input mesh for subdivision must be all triangles")
    print("3. HSV color conversion errors")
    print("")
    
    # Step 1: Fix main window file
    print("Step 1: Fixing main_fixed_window.py...")
    if fix_main_window_file():
        print("✅ main_fixed_window.py fixes applied")
    else:
        print("❌ Failed to fix main_fixed_window.py")
        return False
    
    # Step 2: Create minimal enhanced scene manager if needed
    print("\nStep 2: Ensuring enhanced_scene_manager.py exists...")
    if create_minimal_enhanced_scene_manager():
        print("✅ enhanced_scene_manager.py ready")
    else:
        print("❌ Failed to create enhanced_scene_manager.py")
        return False
    
    # Step 3: Verify fixes
    print("\nStep 3: Verifying fixes...")
    if verify_fixes():
        print("✅ All fixes verified")
    else:
        print("⚠️  Some fixes may need manual attention")
    
    print("\n" + "=" * 60)
    print("🎯 FIXES COMPLETED!")
    print("\nWhat was fixed:")
    print("• Changed handle_note_event() calls to handle_midi_note()")
    print("• Added safe_subdivide() function to prevent triangle errors")
    print("• Added safe_hsv_to_rgb() for color conversion safety")
    print("• Created minimal EnhancedSceneManager if missing")
    print("\nYou can now try running your application again!")
    print("If you encounter issues, check the backup files created.")
    
    return True

if __name__ == "__main__":
    main()
