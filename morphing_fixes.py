# Add this function to your standalone_app.py to fix morphing
# Replace the blend_meshes_simple function with this improved version:

def blend_meshes_simple(meshes, source_key, target_key, alpha):
    """Improved mesh blending with vertex count matching."""
    if source_key not in meshes or target_key not in meshes:
        print(f"Warning: Mesh keys not found: {source_key}, {target_key}")
        return meshes[source_key].points if source_key in meshes else None
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    # Check vertex compatibility
    if source_mesh.n_points != target_mesh.n_points:
        print(f"Resampling meshes: {source_mesh.n_points} -> {target_mesh.n_points}")
        
        # Use the source mesh vertex count as reference
        target_points = source_mesh.n_points
        
        # Resample target mesh to match source
        try:
            if target_mesh.n_points > target_points:
                # Decimate target mesh
                ratio = target_points / target_mesh.n_points
                resampled_target = target_mesh.decimate(1 - ratio)
            else:
                # Subdivide target mesh
                resampled_target = target_mesh.copy()
                while resampled_target.n_points < target_points * 0.8:
                    resampled_target = resampled_target.subdivide(1)
                
                # Fine-tune with decimation if needed
                if resampled_target.n_points > target_points:
                    ratio = target_points / resampled_target.n_points
                    resampled_target = resampled_target.decimate(1 - ratio)
            
            # Now try blending with resampled mesh
            if resampled_target.n_points == source_mesh.n_points:
                source_points = source_mesh.points
                target_points = resampled_target.points
                return (1 - alpha) * source_points + alpha * target_points
            else:
                print(f"Still mismatched after resampling: {resampled_target.n_points} vs {source_mesh.n_points}")
                return source_mesh.points
                
        except Exception as e:
            print(f"Resampling failed: {e}")
            return source_mesh.points
    
    # Linear interpolation for compatible meshes
    source_points = source_mesh.points
    target_points = target_mesh.points
    return (1 - alpha) * source_points + alpha * target_points

# Or for an even simpler solution, you can create meshes with the same resolution:
def create_matched_meshes(resolution=30):
    """Create meshes with matched vertex counts."""
    try:
        # Create all shapes with the same resolution
        meshes = {}
        
        # Base sphere
        sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
        meshes['sphere'] = sphere
        target_points = sphere.n_points
        
        print(f"Target vertex count: {target_points}")
        
        # Create cube and resample to match sphere
        cube = pv.Cube()
        cube_subdivided = cube.subdivide(3)  # Increase resolution
        if cube_subdivided.n_points > target_points:
            ratio = target_points / cube_subdivided.n_points
            meshes['cube'] = cube_subdivided.decimate(1 - ratio)
        else:
            meshes['cube'] = cube_subdivided
        
        # Create cone and resample
        cone = pv.Cone(resolution=resolution)
        cone_subdivided = cone.subdivide(2)
        if cone_subdivided.n_points > target_points:
            ratio = target_points / cone_subdivided.n_points
            meshes['cone'] = cone_subdivided.decimate(1 - ratio)
        else:
            meshes['cone'] = cone_subdivided
        
        # Create cylinder
        try:
            cylinder = pv.Cylinder(resolution=resolution)
            cylinder_subdivided = cylinder.subdivide(2)
            if cylinder_subdivided.n_points > target_points:
                ratio = target_points / cylinder_subdivided.n_points
                meshes['cylinder'] = cylinder_subdivided.decimate(1 - ratio)
            else:
                meshes['cylinder'] = cylinder_subdivided
        except:
            pass
        
        # Print final vertex counts
        for name, mesh in meshes.items():
            print(f"{name}: {mesh.n_points} vertices")
        
        return meshes
        
    except Exception as e:
        print(f"Error creating matched meshes: {e}")
        # Fallback to basic shapes
        return {
            'sphere': pv.Sphere(),
            'cube': pv.Cube()
        }

# To use this fix:
# 1. Replace the create_simple_meshes function call in _initialize_visualization with:
#    self.initial_meshes = create_matched_meshes(30)
# 2. Or replace the blend_meshes_simple function with the improved version above
