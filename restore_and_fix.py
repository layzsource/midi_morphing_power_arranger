#!/usr/bin/env python3
"""
Restore visualizer.py from backup and apply the triangulation fix
"""

import os
import sys

def restore_from_backup():
    """Restore visualizer.py from backup"""
    if os.path.exists("visualizer.py.backup"):
        print("Found backup file, restoring...")
        with open("visualizer.py.backup", 'r') as f:
            backup_content = f.read()
        
        with open("visualizer.py", 'w') as f:
            f.write(backup_content)
        
        print("✅ Restored visualizer.py from backup")
        return True
    else:
        print("❌ No backup file found")
        return False

def apply_simple_fix():
    """Apply a simple fix by just replacing the problematic line"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return False
    
    print("Reading visualizer.py...")
    with open("visualizer.py", 'r') as f:
        lines = f.readlines()
    
    # Find the _resample_mesh_to_match method
    method_start = None
    for i, line in enumerate(lines):
        if "def _resample_mesh_to_match" in line:
            method_start = i
            break
    
    if method_start is None:
        print("❌ Could not find _resample_mesh_to_match method")
        return False
    
    print(f"Found method at line {method_start + 1}")
    
    # Find the end of the method (next method or class definition)
    method_end = None
    for i in range(method_start + 1, len(lines)):
        line = lines[i].strip()
        # Look for next method at same indentation level or class definition
        if line.startswith("def ") and not lines[i].startswith("        "):
            method_end = i
            break
        elif line.startswith("class "):
            method_end = i
            break
        elif i == len(lines) - 1:  # End of file
            method_end = i + 1
            break
    
    if method_end is None:
        method_end = len(lines)
    
    print(f"Method spans lines {method_start + 1} to {method_end}")
    
    # Create the fixed method
    fixed_method = '''    def _resample_mesh_to_match(self, mesh_to_resample, reference_mesh):
        """Resample a mesh to match the vertex count of a reference mesh."""
        target_count = reference_mesh.n_points
        current_count = mesh_to_resample.n_points
        
        result_mesh = mesh_to_resample.copy()
        
        try:
            # CRITICAL FIX: Triangulate BEFORE subdivision
            result_mesh = result_mesh.triangulate()
            result_mesh = result_mesh.clean()
            
            if current_count == target_count:
                return result_mesh
            
            # Increase vertices if needed
            elif current_count < target_count:
                for _ in range(3):  # Max 3 subdivision attempts
                    try:
                        if result_mesh.n_points < target_count * 0.8:
                            result_mesh = result_mesh.subdivide(1)
                        else:
                            break
                    except Exception:
                        break
            
            # Reduce vertices if needed
            if result_mesh.n_points > target_count:
                ratio = target_count / result_mesh.n_points
                try:
                    result_mesh = result_mesh.decimate(1 - ratio)
                except Exception:
                    pass
            
            return result_mesh
            
        except Exception as e:
            print(f"Mesh resampling error: {e}")
            return reference_mesh.copy()

'''
    
    # Replace the method
    new_lines = lines[:method_start] + [fixed_method] + lines[method_end:]
    
    # Write the fixed file
    with open("visualizer.py", 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Applied triangulation fix to visualizer.py")
    return True

def verify_syntax():
    """Check if the Python file has valid syntax"""
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
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def main():
    print("=== Fixing visualizer.py triangulation issue ===")
    
    # Step 1: Try to restore from backup
    if not restore_from_backup():
        print("No backup found, working with current file...")
    
    # Step 2: Apply the fix
    if not apply_simple_fix():
        print("❌ Failed to apply fix")
        return 1
    
    # Step 3: Verify syntax
    if not verify_syntax():
        print("❌ Syntax errors remain. Manual editing required.")
        return 1
    
    print("🎉 Successfully fixed visualizer.py!")
    print("\nThe fix:")
    print("- Added .triangulate() before .subdivide() calls")
    print("- Added proper error handling")
    print("- Simplified the mesh resampling logic")
    print("\nYou can now run your application!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
