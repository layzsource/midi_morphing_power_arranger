# Replace your _apply_morphing method temporarily with this simplified version
# to test if basic morphing works

@performance_monitor
def _apply_morphing_simple_test(self, alpha):
    """Simplified morphing test - bypasses scene manager completely."""
    try:
        print(f"Testing morphing with alpha={alpha}")
        
        # Force fallback to single object mode for testing
        if not hasattr(self, 'test_mesh') or not hasattr(self, 'test_actor'):
            # Create a simple test sphere
            import pyvista as pv
            self.test_mesh = pv.Sphere(radius=1.0, theta_resolution=30, phi_resolution=30)
            self.test_actor = self.plotter_widget.add_mesh(
                self.test_mesh,
                color='red',
                show_edges=True,
                smooth_shading=True
            )
            print("Created test mesh and actor")
        
        # Test morphing between sphere and cube
        if hasattr(self, 'initial_meshes') and 'sphere' in self.initial_meshes and 'cube' in self.initial_meshes:
            from geometry import blend_meshes
            
            blended_points = blend_meshes(
                self.initial_meshes,
                'sphere',
                'cube', 
                alpha
            )
            
            print(f"Blended points shape: {blended_points.shape}")
            
            # Update the test mesh
            self.test_mesh.points = blended_points
            
            # Update color based on morph amount
            morph_color = [1.0 - alpha, alpha, 0.0]  # Red to green
            
            # Remove old actor and add new one
            self.plotter_widget.remove_actor(self.test_actor)
            self.test_actor = self.plotter_widget.add_mesh(
                self.test_mesh,
                color=morph_color,
                show_edges=True,
                smooth_shading=True
            )
            
            # Force render
            self.plotter_widget.render()
            
            print(f"Morphing applied successfully, alpha={alpha}")
            
        else:
            print("ERROR: Initial meshes not available for morphing test")
            if hasattr(self, 'initial_meshes'):
                print(f"Available meshes: {list(self.initial_meshes.keys())}")
            else:
                print("No initial_meshes attribute found")
        
    except Exception as e:
        print(f"ERROR in simple morphing test: {e}")
        import traceback
        traceback.print_exc()

# Also add this method to reset your visualization
def reset_visualization_simple(self):
    """Reset to a simple, clean visualization for testing."""
    try:
        # Clear everything
        self.plotter_widget.clear()
        
        # Create a simple sphere to start
        import pyvista as pv
        sphere = pv.Sphere(radius=1.0, theta_resolution=50, phi_resolution=50)
        actor = self.plotter_widget.add_mesh(
            sphere,
            color='lightblue',
            smooth_shading=True,
            show_edges=False
        )
        
        # Store for testing
        self.test_mesh = sphere
        self.test_actor = actor
        
        # Reset camera
        self.plotter_widget.reset_camera()
        self.plotter_widget.render()
        
        print("Visualization reset to simple sphere")
        
    except Exception as e:
        print(f"Error resetting visualization: {e}")

# Add these methods to your window class and try:
# 1. Call window.reset_visualization_simple() to get a clean start
# 2. Replace _apply_morphing with _apply_morphing_simple_test temporarily  
# 3. Test the morph slider to see if basic morphing works
