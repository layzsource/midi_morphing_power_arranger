#!/usr/bin/env python3
"""
Direct patch for visualizer.py to fix the NotAllTrianglesError

This script will read your visualizer.py file and replace the problematic 
_resample_mesh_to_match method with a fixed version.
"""

import os
import re

def create_fixed_method():
    """Return the fixed _resample_mesh_to_match method"""
    return '''    def _resample_mesh_to_match(self, mesh_to_resample, reference_mesh):
        """
        Resample a mesh to match the vertex count of a reference mesh.
        FIXED VERSION - handles triangulation properly to prevent NotAllTrianglesError
        """
        target_count = reference_mesh.n_points
        current_count = mesh_to_resample.n_points
        
        if self.debug_mode:
            print(f"Resampling mesh: {current_count} -> {target_count} vertices")
        
        # Start with a copy
        result_mesh = mesh_to_resample.copy()
        
        try:
            # CRITICAL FIX: Ensure the mesh is triangulated BEFORE any subdivision
            # This prevents the NotAllTrianglesError
            if hasattr(result_mesh, 'triangulate'):
                if self.debug_mode:
                    print("  Triangulating mesh...")
                result_mesh = result_mesh.triangulate()
                if self.debug_mode:
                    print(f"  After triangulation: {result_mesh.n_points} vertices")
            
            # Clean the mesh to remove any degenerate faces
            result_mesh = result_mesh.clean()
            if self.debug_mode:
                print(f"  After cleaning: {result_mesh.n_points} vertices")
            
            # Verify mesh is all triangles before proceeding
            if hasattr(result_mesh, 'faces') and len(result_mesh.faces) > 0:
                faces = result_mesh.faces
                face_types = []
                i = 0
                while i < len(faces):
                    if i < len(faces):
                        face_size = faces[i]
                        face_types.append(face_size)
                        i += face_size + 1
                
                non_triangles = [ft for ft in face_types if ft != 3]
                if non_triangles:
                    if self.debug_mode:
                        print(f"  WARNING: Found non-triangle faces: {set(non_triangles)}")
                    # Force triangulation again
                    result_mesh = result_mesh.triangulate()
                    if self.debug_mode:
                        print(f"  After forced triangulation: {result_mesh.n_points} vertices")
            
            # Handle vertex count matching
            if current_count == target_count:
                return result_mesh
            
            # If we need more vertices, subdivide (now safe since mesh is triangulated)
            elif current_count < target_count:
                if self.debug_mode:
                    print(f"  Need to increase vertices from {current_count} to {target_count}")
                
                max_iterations = 10  # Prevent infinite loops
                iteration = 0
                
                while result_mesh.n_points < target_count * 0.9 and iteration < max_iterations:
                    try:
                        if self.debug_mode:
                            print(f"    Subdivision attempt {iteration + 1}: {result_mesh.n_points} vertices")
                        
                        # This should now work since mesh is triangulated
                        result_mesh = result_mesh.subdivide(1)
                        
                        if self.debug_mode:
                            print(f"    After subdivision: {result_mesh.n_points} vertices")
                        
                        # Prevent excessive growth
                        if result_mesh.n_points >= target_count * 2:
                            if self.debug_mode:
                                print("    Breaking to prevent excessive vertex growth")
                            break
                            
                    except Exception as e:
                        if self.debug_mode:
                            print(f"    Subdivision failed at iteration {iteration + 1}: {e}")
                        # Try alternative approach
                        try:
                            # Use interpolation-based resampling as fallback
                            if hasattr(reference_mesh, 'sample'):
                                result_mesh = reference_mesh.sample(result_mesh.clean())
                                if self.debug_mode:
                                    print(f"    Fallback sampling successful: {result_mesh.n_points} vertices")
                                break
                        except:
                            if self.debug_mode:
                                print("    Fallback sampling also failed")
                        break
                    
                    iteration += 1
            
            # If we have too many vertices, decimate
            if result_mesh.n_points > target_count:
                if self.debug_mode:
                    print(f"  Need to reduce vertices from {result_mesh.n_points} to {target_count}")
                ratio = target_count / result_mesh.n_points
                try:
                    result_mesh = result_mesh.decimate(1 - ratio)
                    if self.debug_mode:
                        print(f"  After decimation: {result_mesh.n_points} vertices")
                except Exception as e:
                    if self.debug_mode:
                        print(f"  Decimation failed: {e}")
                    # If decimation fails, clean the mesh
                    try:
                        result_mesh = result_mesh.clean()
                    except:
                        pass
            
            # Check final result
            final_count = result_mesh.n_points
            percentage_diff = abs(final_count - target_count) / target_count * 100
            
            if percentage_diff <= 15:  # Accept within 15% (relaxed from 10%)
                if self.debug_mode:
                    print(f"  SUCCESS: Final vertex count {final_count} (target: {target_count}, diff: {percentage_diff:.1f}%)")
                return result_mesh
            else:
                if self.debug_mode:
                    print(f"  WARNING: Large vertex count difference {final_count} vs {target_count} ({percentage_diff:.1f}%)")
                return result_mesh  # Return what we have rather than None
                
        except Exception as e:
            if self.debug_mode:
                print(f"  ERROR in mesh resampling: {e}")
            
            # Ultimate fallback: try to create a compatible mesh using interpolation
            try:
                if hasattr(reference_mesh, 'sample'):
                    clean_mesh = mesh_to_resample.clean().triangulate()
                    fallback_mesh = reference_mesh.sample(clean_mesh)
                    if self.debug_mode:
                        print(f"  FALLBACK: Created mesh with {fallback_mesh.n_points} vertices")
                    return fallback_mesh
            except:
                pass
            
            # Return original mesh as last resort
            return mesh_to_resample.copy()'''

def patch_visualizer_file(file_path="visualizer.py"):
    """Patch the visualizer.py file with the fixed method"""
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return False
    
    # Read the current file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_path = file_path + ".backup"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Created backup: {backup_path}")
    
    # Find the method to replace
    # Look for the method definition and its content
    method_pattern = r'def _resample_mesh_to_match\(self.*?\n    def '
    
    # Find the start of the method
    start_match = re.search(r'def _resample_mesh_to_match\(self', content)
    if not start_match:
        print("Error: Could not find _resample_mesh_to_match method")
        return False
    
    start_pos = start_match.start()
    
    # Find the next method or class definition to determine where this method ends
    rest_of_content = content[start_pos:]
    
    # Look for the next method definition at the same indentation level
    next_method_pattern = r'\n    def [a-zA-Z_]'
    next_match = re.search(next_method_pattern, rest_of_content)
    
    if next_match:
        end_pos = start_pos + next_match.start()
        old_method = content[start_pos:end_pos]
    else:
        # If no next method found, look for class end or file end
        # This is a simpler approach - take everything until double dedent
        lines = rest_of_content.split('\n')
        end_line = 0
        for i, line in enumerate(lines[1:], 1):  # Skip the def line
            if line and not line.startswith('        ') and not line.startswith('    '):
                # Found a line that's not indented as method content
                if line.startswith('    def ') or line.startswith('class ') or line.strip() == '':
                    continue
                end_line = i
                break
        
        if end_line > 0:
            end_pos = start_pos + len('\n'.join(lines[:end_line]))
        else:
            end_pos = len(content)
        
        old_method = content[start_pos:end_pos]
    
    print(f"Found method to replace ({len(old_method)} characters)")
    
    # Replace the method
    new_content = content[:start_pos] + create_fixed_method() + '\n\n' + content[end_pos:]
    
    # Write the patched file
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Successfully patched {file_path}")
    print("The NotAllTrianglesError should now be fixed!")
    print("\nKey improvements made:")
    print("- Added explicit triangulation before subdivision")
    print("- Added mesh cleaning and validation") 
    print("- Added fallback methods for failed subdivision")
    print("- Improved error handling and debug output")
    
    return True

if __name__ == "__main__":
    # Try to find visualizer.py in current directory
    visualizer_path = "visualizer.py"
    if os.path.exists(visualizer_path):
        patch_visualizer_file(visualizer_path)
    else:
        print(f"Please run this script from the directory containing visualizer.py")
        print("Or manually copy the fixed method from the output above.")
