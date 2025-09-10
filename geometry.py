"""
Fixed Mesh Morphing System - Resolves vertex count mismatch errors
Ensures all meshes have identical vertex counts for proper morphing
"""

import numpy as np
import pyvista as pv
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class MeshMorphingSystem:
    """Robust mesh morphing system with vertex count synchronization."""
    
    def __init__(self, resolution: int = 30):
        self.resolution = resolution
        self.meshes = {}
        self.reference_vertex_count = None
        self.create_synchronized_meshes()
    
    def create_synchronized_meshes(self) -> Dict[str, pv.PolyData]:
        """Create all meshes with identical vertex counts."""
        logger.info(f"Creating synchronized meshes with resolution {self.resolution}")
        
        # Create base sphere as reference
        base_sphere = pv.Sphere(
            radius=1.0,
            phi_resolution=self.resolution,
            theta_resolution=self.resolution
        )
        
        # Store reference vertex count
        self.reference_vertex_count = base_sphere.n_points
        logger.info(f"Reference vertex count: {self.reference_vertex_count}")
        
        # Store base sphere
        self.meshes['sphere'] = base_sphere
        
        # Create other shapes by deforming the sphere
        # This ensures identical vertex counts
        self.meshes['cube'] = self._create_cube_from_sphere(base_sphere)
        self.meshes['cone'] = self._create_cone_from_sphere(base_sphere)
        self.meshes['torus'] = self._create_torus_from_sphere(base_sphere)
        self.meshes['icosahedron'] = self._create_icosahedron_from_sphere(base_sphere)
        
        # Verify all meshes have same vertex count
        self._verify_vertex_counts()
        
        return self.meshes
    
    def _create_cube_from_sphere(self, sphere: pv.PolyData) -> pv.PolyData:
        """Transform sphere vertices into cube shape."""
        points = sphere.points.copy()
        
        # Normalize points
        normalized = points / np.linalg.norm(points, axis=1, keepdims=True)
        
        # Project to cube faces using infinity norm
        x, y, z = normalized[:, 0], normalized[:, 1], normalized[:, 2]
        max_coord = np.maximum(np.maximum(np.abs(x), np.abs(y)), np.abs(z))
        
        # Scale back to cube
        cube_points = normalized / max_coord[:, np.newaxis]
        
        # Create new mesh with same topology
        cube = sphere.copy()
        cube.points = cube_points
        
        return cube
    
    def _create_cone_from_sphere(self, sphere: pv.PolyData) -> pv.PolyData:
        """Transform sphere vertices into cone shape."""
        points = sphere.points.copy()
        
        # Convert to cylindrical coordinates
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        r = np.sqrt(x**2 + y**2)
        
        # Create cone shape: radius decreases linearly with height
        height = (z + 1) / 2  # Normalize z from [-1,1] to [0,1]
        cone_radius = 1 - height * 0.8  # Taper to 20% at top
        
        # Apply cone transformation
        scale_factor = cone_radius / (r + 1e-10)
        cone_points = points.copy()
        cone_points[:, 0] *= scale_factor
        cone_points[:, 1] *= scale_factor
        
        # Create new mesh
        cone = sphere.copy()
        cone.points = cone_points
        
        return cone
    
    def _create_torus_from_sphere(self, sphere: pv.PolyData) -> pv.PolyData:
        """Transform sphere vertices into torus shape."""
        points = sphere.points.copy()
        
        # Spherical to toroidal mapping
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Calculate spherical coordinates
        r = np.sqrt(x**2 + y**2 + z**2)
        theta = np.arctan2(y, x)
        phi = np.arccos(np.clip(z / (r + 1e-10), -1, 1))
        
        # Torus parameters
        major_radius = 0.7
        minor_radius = 0.3
        
        # Map to torus
        torus_r = major_radius + minor_radius * np.cos(phi * 2)
        torus_z = minor_radius * np.sin(phi * 2)
        
        torus_points = np.column_stack([
            torus_r * np.cos(theta),
            torus_r * np.sin(theta),
            torus_z
        ])
        
        # Create new mesh
        torus = sphere.copy()
        torus.points = torus_points
        
        return torus
    
    def _create_icosahedron_from_sphere(self, sphere: pv.PolyData) -> pv.PolyData:
        """Transform sphere vertices into icosahedron-like shape."""
        points = sphere.points.copy()
        
        # Normalize points
        normalized = points / np.linalg.norm(points, axis=1, keepdims=True)
        
        # Quantize directions to create faceted appearance
        # This creates an icosahedron-like polyhedron
        quantization_level = 5
        quantized = np.round(normalized * quantization_level) / quantization_level
        
        # Renormalize to unit sphere
        quantized = quantized / np.linalg.norm(quantized, axis=1, keepdims=True)
        
        # Create new mesh
        icosahedron = sphere.copy()
        icosahedron.points = quantized
        
        return icosahedron
    
    def _verify_vertex_counts(self):
        """Verify all meshes have identical vertex counts."""
        counts = {}
        for name, mesh in self.meshes.items():
            counts[name] = mesh.n_points
            logger.debug(f"Mesh '{name}': {mesh.n_points} vertices")
        
        unique_counts = set(counts.values())
        if len(unique_counts) > 1:
            error_msg = f"Vertex count mismatch detected: {counts}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"✓ All meshes have {self.reference_vertex_count} vertices")
    
    def blend_meshes(self, source_key: str, target_key: str, alpha: float) -> np.ndarray:
        """Safely blend between two meshes."""
        if source_key not in self.meshes:
            raise KeyError(f"Source mesh '{source_key}' not found")
        if target_key not in self.meshes:
            raise KeyError(f"Target mesh '{target_key}' not found")
        
        source_mesh = self.meshes[source_key]
        target_mesh = self.meshes[target_key]
        
        # Double-check vertex counts
        if source_mesh.n_points != target_mesh.n_points:
            error_msg = (f"Vertex count mismatch: {source_key}({source_mesh.n_points}) "
                        f"vs {target_key}({target_mesh.n_points})")
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Perform linear interpolation
        alpha = np.clip(alpha, 0.0, 1.0)
        source_points = source_mesh.points
        target_points = target_mesh.points
        
        blended_points = (1 - alpha) * source_points + alpha * target_points
        
        return blended_points


class AdvancedMorphingSystem(MeshMorphingSystem):
    """Advanced morphing with animation and error recovery."""
    
    def __init__(self, resolution: int = 30):
        super().__init__(resolution)
        self.current_points = None
        self.original_points = None
        self.target_points = None
        self.morph_progress = 0.0
        self.morph_speed = 1.0
        self.is_morphing = False
    
    def start_morph(self, source_key: str, target_key: str, speed: float = 1.0):
        """Start morphing animation between two meshes."""
        try:
            if source_key not in self.meshes or target_key not in self.meshes:
                logger.error(f"Invalid mesh keys: {source_key}, {target_key}")
                return False
            
            source_mesh = self.meshes[source_key]
            target_mesh = self.meshes[target_key]
            
            # Verify compatibility
            if source_mesh.n_points != target_mesh.n_points:
                logger.error(f"Cannot morph: vertex count mismatch "
                           f"({source_mesh.n_points} vs {target_mesh.n_points})")
                return False
            
            self.original_points = source_mesh.points.copy()
            self.target_points = target_mesh.points.copy()
            self.current_points = self.original_points.copy()
            self.morph_progress = 0.0
            self.morph_speed = speed
            self.is_morphing = True
            
            logger.info(f"Started morph: {source_key} → {target_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start morph: {e}")
            return False
    
    def animate_morph(self, dt: float) -> Optional[np.ndarray]:
        """Animate morphing with proper error handling."""
        if not self.is_morphing:
            return self.current_points
        
        try:
            # Verify arrays are valid
            if (self.original_points is None or 
                self.target_points is None or
                len(self.original_points) == 0 or 
                len(self.target_points) == 0):
                logger.error("Invalid morph state - arrays are None or empty")
                self.is_morphing = False
                return self.current_points
            
            # Check shape compatibility
            if self.original_points.shape != self.target_points.shape:
                logger.error(f"Shape mismatch during morph: "
                           f"{self.original_points.shape} vs {self.target_points.shape}")
                self.is_morphing = False
                return self.current_points
            
            # Update morph progress
            self.morph_progress += dt * self.morph_speed
            
            if self.morph_progress >= 1.0:
                self.morph_progress = 1.0
                self.is_morphing = False
            
            # Perform interpolation
            t = self.morph_progress
            self.current_points = (1 - t) * self.original_points + t * self.target_points
            
            return self.current_points
            
        except Exception as e:
            logger.error(f"Error during morph animation: {e}")
            self.is_morphing = False
            return self.current_points
    
    def set_morph_blend(self, source_key: str, target_key: str, alpha: float) -> np.ndarray:
        """Set morphing to a specific blend value (0-1)."""
        try:
            blended = self.blend_meshes(source_key, target_key, alpha)
            self.current_points = blended
            return blended
        except Exception as e:
            logger.error(f"Blend failed: {e}")
            # Return current points as fallback
            if self.current_points is not None:
                return self.current_points
            # Final fallback: return sphere points
            return self.meshes['sphere'].points


# Patch for existing code - Drop-in replacement
def create_initial_meshes(resolution: int = 30) -> Dict[str, pv.PolyData]:
    """Create initial meshes with guaranteed identical vertex counts."""
    morph_system = MeshMorphingSystem(resolution)
    return morph_system.meshes


def safe_blend_meshes(meshes: Dict[str, pv.PolyData], 
                      source_key: str, 
                      target_key: str, 
                      alpha: float) -> np.ndarray:
    """Safe mesh blending with error recovery."""
    try:
        if source_key not in meshes or target_key not in meshes:
            logger.error(f"Mesh keys not found: {source_key}, {target_key}")
            # Fallback to first available mesh
            fallback_key = list(meshes.keys())[0]
            return meshes[fallback_key].points
        
        source_mesh = meshes[source_key]
        target_mesh = meshes[target_key]
        
        # Check vertex counts
        if source_mesh.n_points != target_mesh.n_points:
            logger.error(f"Vertex mismatch: {source_mesh.n_points} vs {target_mesh.n_points}")
            
            # Try to fix by recreating meshes
            logger.info("Attempting to recreate meshes with matching vertex counts...")
            morph_system = MeshMorphingSystem()
            
            if source_key in morph_system.meshes and target_key in morph_system.meshes:
                return morph_system.blend_meshes(source_key, target_key, alpha)
            else:
                # Final fallback
                return source_mesh.points
        
        # Normal blending
        alpha = np.clip(alpha, 0.0, 1.0)
        return (1 - alpha) * source_mesh.points + alpha * target_mesh.points
        
    except Exception as e:
        logger.error(f"Blend failed with error: {e}")
        # Ultimate fallback - return source mesh points
        if source_key in meshes:
            return meshes[source_key].points
        # Or first available mesh
        return list(meshes.values())[0].points


# Integration fix for main_window.py
class MorphingWindowFix:
    """Fix for the morphing window to prevent vertex count mismatches."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.morph_system = AdvancedMorphingSystem()
        self.apply_fixes()
    
    def apply_fixes(self):
        """Apply fixes to the main window."""
        # Replace meshes with synchronized versions
        self.main_window.meshes = self.morph_system.meshes
        
        # Replace morphing methods
        self.main_window.adv_morphing = self.morph_system
        
        # Patch the animate_frame method
        original_animate = self.main_window.animate_frame
        
        def safe_animate_frame():
            try:
                # Call morphing with error handling
                if hasattr(self.main_window, 'adv_morphing'):
                    dt = 0.016  # Assume 60 FPS
                    points = self.morph_system.animate_morph(dt)
                    
                    if points is not None and self.main_window.actor:
                        # Update mesh points
                        mesh = self.main_window.actor.GetMapper().GetInput()
                        mesh.GetPoints().SetData(pv.numpy_to_vtk(points))
                        mesh.Modified()
                        self.main_window.plotter.render()
                else:
                    # Fallback to original
                    original_animate()
                    
            except Exception as e:
                logger.error(f"Animation frame error: {e}")
        
        self.main_window.animate_frame = safe_animate_frame
        
        logger.info("✓ Morphing fixes applied")


# Quick fix function to be called from main.py
def fix_morphing_errors(main_window):
    """Quick fix function to resolve morphing errors in existing application."""
    try:
        fixer = MorphingWindowFix(main_window)
        logger.info("✓ Morphing system fixed and ready")
        return True
    except Exception as e:
        logger.error(f"Failed to apply morphing fixes: {e}")
        return False


# Test the fix
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Testing mesh morphing system...")
    print("-" * 50)
    
    # Test basic system
    morph_system = MeshMorphingSystem(resolution=25)
    print(f"Created {len(morph_system.meshes)} meshes")
    
    # Test blending
    for i, (source, target) in enumerate([
        ('sphere', 'cube'),
        ('cube', 'cone'),
        ('cone', 'torus'),
        ('torus', 'icosahedron'),
        ('icosahedron', 'sphere')
    ]):
        try:
            blended = morph_system.blend_meshes(source, target, 0.5)
            print(f"✓ Blend test {i+1}: {source} → {target} (shape: {blended.shape})")
        except Exception as e:
            print(f"✗ Blend test {i+1} failed: {e}")
    
    print("-" * 50)
    
    # Test advanced system
    adv_system = AdvancedMorphingSystem()
    
    # Test morphing animation
    if adv_system.start_morph('sphere', 'cube', speed=2.0):
        print("✓ Started morph animation")
        
        # Simulate animation frames
        for frame in range(10):
            points = adv_system.animate_morph(0.1)
            if points is not None:
                print(f"  Frame {frame+1}: progress={adv_system.morph_progress:.2f}")
    
    print("-" * 50)
    print("✓ All tests completed")
