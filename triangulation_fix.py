#!/usr/bin/env python3
"""
Fix for the NotAllTrianglesError in visualizer.py

This script will replace the problematic _resample_mesh_to_match method
with a robust version that ensures triangulation before subdivision.
"""

def fixed_resample_mesh_to_match(self, mesh_to_resample, reference_mesh):
    """
    Fixed version of _resample_mesh_to_match that handles triangulation properly.
    """
    target_count = reference_mesh.n_points
    current_count = mesh_to_resample.n_points
    
    print(f"Resampling mesh: {current_count} -> {target_count} vertices")
    
    # Start with a copy
    result_mesh = mesh_to_resample.copy()
    
    try:
        # CRITICAL: Ensure the mesh is triangulated BEFORE any subdivision
        # This is what was missing and causing the NotAllTrianglesError
        if hasattr(result_mesh, 'triangulate'):
            print("  Triangulating mesh...")
            result_mesh = result_mesh.triangulate()
            print(f"  After triangulation: {result_mesh.n_points} vertices")
        
        # Clean the mesh to remove any degenerate faces
        result_mesh = result_mesh.clean()
        print(f"  After cleaning: {result_mesh.n_points} vertices")
        
        # Check if mesh is all triangles
        if hasattr(result_mesh, 'faces'):
            # Get face types - triangles should be type 3 followed by 3 vertex indices
            faces = result_mesh.faces
            if len(faces) > 0:
                # Check face structure
                face_types = []
                i = 0
                while i < len(faces):
                    if i < len(faces):
                        face_size = faces[i]
                        face_types.append(face_size)
                        i += face_size + 1
                
                non_triangles = [ft for ft in face_types if ft != 3]
                if non_triangles:
                    print(f"  WARNING: Found non-triangle faces: {set(non_triangles)}")
                    # Force triangulation again
                    result_mesh = result_mesh.triangulate()
                    print(f"  After forced triangulation: {result_mesh.n_points} vertices")
        
        # Now handle vertex count matching
        if current_count == target_count:
            return result_mesh
        
        # If we need more vertices, subdivide
        elif current_count < target_count:
            print(f"  Need to increase vertices from {current_count} to {target_count}")
            
            max_iterations = 10  # Prevent infinite loops
            iteration = 0
            
            while result_mesh.n_points < target_count * 0.9 and iteration < max_iterations:
                try:
                    print(f"    Subdivision attempt {iteration + 1}: {result_mesh.n_points} vertices")
                    result_mesh = result_mesh.subdivide(1)
                    print(f"    After subdivision: {result_mesh.n_points} vertices")
                    
                    # Prevent excessive growth
                    if result_mesh.n_points >= target_count * 2:
                        print("    Breaking to prevent excessive vertex growth")
                        break
                        
                except Exception as e:
                    print(f"    Subdivision failed at iteration {iteration + 1}: {e}")
                    break
                
                iteration += 1
        
        # If we have too many vertices, decimate
        if result_mesh.n_points > target_count:
            print(f"  Need to reduce vertices from {result_mesh.n_points} to {target_count}")
            ratio = target_count / result_mesh.n_points
            try:
                result_mesh = result_mesh.decimate(1 - ratio)
                print(f"  After decimation: {result_mesh.n_points} vertices")
            except Exception as e:
                print(f"  Decimation failed: {e}")
                # If decimation fails, try a simpler approach
                try:
                    # Use extract_points with a simpler selection
                    result_mesh = result_mesh.clean()
                except:
                    pass
        
        # Check final result
        final_count = result_mesh.n_points
        percentage_diff = abs(final_count - target_count) / target_count * 100
        
        if percentage_diff <= 10:  # Accept within 10%
            print(f"  SUCCESS: Final vertex count {final_count} (target: {target_count}, diff: {percentage_diff:.1f}%)")
            return result_mesh
        else:
            print(f"  WARNING: Large vertex count difference {final_count} vs {target_count} ({percentage_diff:.1f}%)")
            return result_mesh  # Return what we have rather than None
            
    except Exception as e:
        print(f"  ERROR in mesh resampling: {e}")
        # Return the original mesh rather than None
        return mesh_to_resample.copy()


# Alternative simplified approach for when subdivision keeps failing
def simplified_resample_mesh_to_match(self, mesh_to_resample, reference_mesh):
    """
    Simplified fallback method that uses interpolation instead of subdivision.
    """
    target_count = reference_mesh.n_points
    
    try:
        # Method 1: Use PyVista's sampling functionality
        if hasattr(reference_mesh, 'sample'):
            # Clean the mesh first
            clean_mesh = mesh_to_resample.clean().triangulate()
            # Sample the target mesh using the reference mesh structure
            resampled = reference_mesh.sample(clean_mesh)
            if resampled.n_points == target_count:
                print(f"  SUCCESS: Resampled using interpolation: {resampled.n_points} vertices")
                return resampled
        
        # Method 2: Create a deformed version of the reference mesh
        # This ensures perfect vertex count matching
        ref_points = reference_mesh.points.copy()
        orig_points = mesh_to_resample.points
        
        # Find bounding boxes
        ref_bounds = reference_mesh.bounds
        orig_bounds = mesh_to_resample.bounds
        
        # Transform reference points to approximate the original shape
        # This is a simple approach - you could make it more sophisticated
        scale_x = (orig_bounds[1] - orig_bounds[0]) / (ref_bounds[1] - ref_bounds[0])
        scale_y = (orig_bounds[3] - orig_bounds[2]) / (ref_bounds[3] - ref_bounds[2])  
        scale_z = (orig_bounds[5] - orig_bounds[4]) / (ref_bounds[5] - ref_bounds[4])
        
        # Apply scaling and translation
        transformed_points = ref_points.copy()
        transformed_points[:, 0] *= scale_x
        transformed_points[:, 1] *= scale_y
        transformed_points[:, 2] *= scale_z
        
        # Create new mesh with reference topology but transformed points
        result_mesh = reference_mesh.copy()
        result_mesh.points = transformed_points
        
        print(f"  SUCCESS: Created deformed mesh: {result_mesh.n_points} vertices")
        return result_mesh
        
    except Exception as e:
        print(f"  ERROR in simplified resampling: {e}")
        return reference_mesh.copy()  # Ultimate fallback


def apply_fix_to_visualizer():
    """
    Instructions for applying this fix to your visualizer.py file.
    """
    print("""
To fix the NotAllTrianglesError in your visualizer.py file:

1. Find the _resample_mesh_to_match method (around line 330-340)
2. Replace it with the fixed_resample_mesh_to_match function above
3. Make sure to update the method signature to match your class

Key changes made:
- Added explicit triangulation BEFORE subdivision
- Added mesh cleaning to remove degenerate faces
- Added face type verification
- Added better error handling
- Added fallback methods if subdivision fails

The fix ensures that:
1. All meshes are triangulated before subdivision attempts
2. Non-triangle faces are detected and handled
3. Fallback methods are available if subdivision fails
4. Better logging for debugging

Try this fix and let me know if you still get the error!
""")

if __name__ == "__main__":
    apply_fix_to_visualizer()
