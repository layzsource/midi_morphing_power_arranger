#!/usr/bin/env python3
"""
Complete fix for vertex count mismatch in visualizer.py

This creates a robust mesh resampling system that ensures all meshes 
have exactly the same vertex count.
"""

import os
import re

def create_robust_mesh_methods():
    """Create the complete set of fixed methods for visualizer.py"""
    
    methods = """
    def _create_initial_meshes(self):
        \"\"\"Create initial meshes with guaranteed matching vertex counts.\"\"\"
        print("Creating meshes with matched vertex counts...")
        
        # Create reference sphere
        resolution = getattr(self, 'resolution', 25)
        sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
        target_count = sphere.n_points
        
        print(f"Target vertex count: {target_count}")
        
        # Store sphere as reference
        self.meshes = {'sphere': sphere}
        
        # Create other shapes by deforming the sphere (guaranteed same vertex count)
        self.meshes['cube'] = self._create_cube_from_sphere(sphere)
        self.meshes['cone'] = self._create_cone_from_sphere(sphere)  
        self.meshes['cylinder'] = self._create_cylinder_from_sphere(sphere)
        self.meshes['torus'] = self._create_torus_from_sphere(sphere)
        
        # Verify all have same vertex count
        counts = {name: mesh.n_points for name, mesh in self.meshes.items()}
        print(f"Final vertex counts: {counts}")
        
        if len(set(counts.values())) == 1:
            print(f"✅ SUCCESS: All meshes have {target_count} vertices")
        else:
            print(f"❌ ERROR: Mismatched vertex counts: {counts}")
            # Fallback: all meshes become sphere variants
            for name in self.meshes:
                if self.meshes[name].n_points != target_count:
                    self.meshes[name] = sphere.copy()
    
    def _create_cube_from_sphere(self, sphere):
        \"\"\"Create cube by deforming sphere points.\"\"\"
        points = sphere.points.copy()
        
        # Normalize to cube shape by scaling each coordinate independently
        max_vals = np.max(np.abs(points), axis=0)
        normalized = points / max_vals
        
        # Create cube by taking sign and scaling
        cube_points = np.sign(normalized) * 0.8
        
        # Smooth transition from sphere to cube
        alpha = 0.7  # How "cube-like" vs "sphere-like"
        final_points = alpha * cube_points + (1 - alpha) * points * 0.8
        
        cube = sphere.copy()
        cube.points = final_points
        return cube
    
    def _create_cone_from_sphere(self, sphere):
        \"\"\"Create cone by deforming sphere points.\"\"\"
        points = sphere.points.copy()
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Convert to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        
        # Create cone shape: radius decreases with height
        height_factor = (z + 1) / 2  # Normalize z from [-1,1] to [0,1]
        cone_radius = (1 - height_factor) * 0.8  # Radius decreases to 0 at top
        
        cone_points = np.column_stack([
            cone_radius * np.cos(theta),
            cone_radius * np.sin(theta),
            z
        ])
        
        cone = sphere.copy()
        cone.points = cone_points
        return cone
    
    def _create_cylinder_from_sphere(self, sphere):
        \"\"\"Create cylinder by deforming sphere points.\"\"\"
        points = sphere.points.copy()
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Convert to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        
        # Create cylinder: constant radius, keep z
        cylinder_radius = 0.8
        
        cylinder_points = np.column_stack([
            cylinder_radius * np.cos(theta),
            cylinder_radius * np.sin(theta),
            z
        ])
        
        cylinder = sphere.copy()
        cylinder.points = cylinder_points
        return cylinder
    
    def _create_torus_from_sphere(self, sphere):
        \"\"\"Create torus by deforming sphere points.\"\"\"
        points = sphere.points.copy()
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Convert to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        
        # Create torus
        major_radius = 0.7
        minor_radius = 0.3
        
        # Map sphere surface to torus surface
        new_r = major_radius + minor_radius * np.cos(z * np.pi * 2)
        new_z = minor_radius * np.sin(z * np.pi * 2)
        
        torus_points = np.column_stack([
            new_r * np.cos(theta),
            new_r * np.sin(theta),
            new_z
        ])
        
        torus = sphere.copy()
        torus.points = torus_points
        return torus
    
    def _resample_mesh_to_match(self, mesh_to_resample, reference_mesh):
        \"\"\"
        FIXED VERSION: Always returns mesh with exact vertex count match.
        Uses deformation approach instead of subdivision/decimation.
        \"\"\"
        target_count = reference_mesh.n_points
        current_count = mesh_to_resample.n_points
        
        if current_count == target_count:
            return mesh_to_resample.copy()
        
        # For mismatched counts, use the reference mesh structure
        # and deform it to approximate the target shape
        try:
            # Get bounding boxes
            ref_bounds = reference_mesh.bounds
            target_bounds = mesh_to_resample.bounds
            
            # Calculate scale factors
            ref_size = [ref_bounds[1] - ref_bounds[0], 
                       ref_bounds[3] - ref_bounds[2], 
                       ref_bounds[5] - ref_bounds[4]]
            target_size = [target_bounds[1] - target_bounds[0],
                          target_bounds[3] - target_bounds[2], 
                          target_bounds[5] - target_bounds[4]]
            
            # Avoid division by zero
            scale = [t/r if r > 0.001 else 1.0 for t, r in zip(target_size, ref_size)]
            
            # Apply scaling to reference mesh points
            scaled_points = reference_mesh.points.copy()
            scaled_points[:, 0] *= scale[0]
            scaled_points[:, 1] *= scale[1] 
            scaled_points[:, 2] *= scale[2]
            
            # Create result mesh with reference topology
            result = reference_mesh.copy()
            result.points = scaled_points
            
            print(f"Resampled mesh: {current_count} -> {result.n_points} vertices (target: {target_count})")
            return result
            
        except Exception as e:
            print(f"Resampling failed: {e}, returning reference mesh")
            return reference_mesh.copy()
    
    def _morph_meshes(self, morph_factor):
        \"\"\"
        FIXED VERSION: Safe morphing with vertex count validation.
        \"\"\"
        if not hasattr(self, 'meshes') or not self.meshes:
            return
        
        current_key = getattr(self, 'current_mesh_key', 'sphere')
        target_key = getattr(self, 'target_mesh_key', 'cube')
        
        # Ensure keys exist
        if current_key not in self.meshes:
            current_key = list(self.meshes.keys())[0]
        if target_key not in self.meshes:
            target_key = list(self.meshes.keys())[0]
        
        current_mesh = self.meshes[current_key]
        target_mesh = self.meshes[target_key]
        
        # CRITICAL: Verify vertex counts match
        if current_mesh.n_points != target_mesh.n_points:
            print(f"ERROR: Vertex count mismatch in morphing!")
            print(f"Current ({current_key}): {current_mesh.n_points}")
            print(f"Target ({target_key}): {target_mesh.n_points}")
            
            # Emergency fix: resample target to match current
            target_mesh = self._resample_mesh_to_match(target_mesh, current_mesh)
            self.meshes[target_key] = target_mesh
            
            # Verify fix worked
            if current_mesh.n_points != target_mesh.n_points:
                print("Emergency resampling failed, skipping morph")
                return
        
        # Safe morphing
        try:
            current_points = current_mesh.points
            target_points = target_mesh.points
            
            # Linear interpolation
            morphed_points = current_points * (1 - morph_factor) + target_points * morph_factor
            
            # Update mesh
            if hasattr(self, 'current_mesh') and self.current_mesh is not None:
                self.current_mesh.points = morphed_points
                
        except Exception as e:
            print(f"Morphing failed: {e}")
"""
    
    return methods

def apply_comprehensive_fix():
    """Apply the complete fix to visualizer.py"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return False
    
    # Read current file
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Create backup
    with open("visualizer.py.backup2", 'w') as f:
        f.write(content)
    print("✅ Created backup: visualizer.py.backup2")
    
    # Add necessary imports at the top
    if "import numpy as np" not in content:
        import_section = content.split('\n')
        for i, line in enumerate(import_section):
            if line.startswith('import ') or line.startswith('from '):
                import_section.insert(i, "import numpy as np")
                break
        content = '\n'.join(import_section)
    
    # Find and replace problematic methods
    methods_to_replace = [
        '_create_initial_meshes',
        '_resample_mesh_to_match', 
        '_morph_meshes'
    ]
    
    new_methods = create_robust_mesh_methods()
    
    # Replace each method
    for method_name in methods_to_replace:
        pattern = rf'def {method_name}\(self.*?\n    def '
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Find method boundaries more carefully
            start_pos = content.find(f'def {method_name}(self')
            if start_pos != -1:
                # Find next method at same indentation
                rest = content[start_pos:]
                lines = rest.split('\n')
                end_line = len(lines)
                
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() and not line.startswith('        ') and not line.startswith('    '):
                        if line.startswith('    def ') or line.startswith('class '):
                            end_line = i
                            break
                
                # Remove old method
                old_method = '\n'.join(lines[:end_line])
                content = content.replace(old_method, "")
                print(f"✅ Removed old {method_name}")
    
    # Add new methods before the last method or class
    insertion_point = content.rfind('\n    def ')
    if insertion_point == -1:
        insertion_point = content.rfind('\nclass ')
    
    if insertion_point != -1:
        content = content[:insertion_point] + new_methods + content[insertion_point:]
    else:
        # Add at end of class
        content = content.rstrip() + new_methods + '\n'
    
    # Write fixed file
    with open("visualizer.py", 'w') as f:
        f.write(content)
    
    print("✅ Applied comprehensive vertex count fix")
    return True

def verify_fix():
    """Verify the fix was applied correctly"""
    try:
        with open("visualizer.py", 'r') as f:
            content = f.read()
        
        compile(content, "visualizer.py", "exec")
        
        # Check for key fixes
        checks = [
            "_create_cube_from_sphere" in content,
            "_create_torus_from_sphere" in content, 
            "n_points != target_mesh.n_points" in content,
            "Emergency fix: resample target" in content
        ]
        
        if all(checks):
            print("✅ All fixes verified successfully")
            return True
        else:
            print(f"⚠️  Some fixes may be missing: {checks}")
            return False
            
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == "__main__":
    print("=== Comprehensive Vertex Count Fix ===")
    
    if apply_comprehensive_fix():
        if verify_fix():
            print("\n🎉 SUCCESS! Your visualizer should now work correctly.")
            print("\nKey improvements:")
            print("- All meshes created by deforming a reference sphere")
            print("- Guaranteed identical vertex counts")
            print("- Safe morphing with vertex count validation") 
            print("- Emergency resampling if mismatches occur")
            print("- Better error handling and debug output")
        else:
            print("\n⚠️  Fix applied but verification failed. Check manually.")
    else:
        print("\n❌ Failed to apply fix")
