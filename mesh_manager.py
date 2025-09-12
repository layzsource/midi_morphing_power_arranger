#!/usr/bin/env python3
"""
Mesh Manager - Complete mesh generation and management system
Provides all geometric shapes, procedural generation, and mesh operations.
Fixed for PyVista compatibility.
"""

import numpy as np
import pyvista as pv
from typing import Dict, Optional, Tuple, List
import time
from dataclasses import dataclass
from enum import Enum


class MeshType(Enum):
    """Available mesh types."""
    SPHERE = "sphere"
    CUBE = "cube"
    ICOSAHEDRON = "icosahedron"
    TORUS = "torus"
    CYLINDER = "cylinder"
    CONE = "cone"
    DODECAHEDRON = "dodecahedron"
    OCTAHEDRON = "octahedron"
    TETRAHEDRON = "tetrahedron"
    PYRAMID = "pyramid"
    DISC = "disc"
    RING = "ring"
    HELIX = "helix"
    MOBIUS = "mobius"
    KLEIN = "klein"
    SUPERTOROID = "supertoroid"
    PARAMETRIC = "parametric"
    FRACTAL = "fractal"


@dataclass
class MeshParameters:
    """Parameters for mesh generation."""
    resolution: int = 50
    radius: float = 1.0
    height: float = 2.0
    inner_radius: float = 0.5
    outer_radius: float = 1.0
    n_sides: int = 6
    n_twists: int = 3
    complexity: int = 3
    noise_amplitude: float = 0.1
    seed: int = 42


class MeshManager:
    """Manages mesh creation, caching, and morphing targets."""
    
    def __init__(self):
        self.meshes: Dict[str, pv.PolyData] = {}
        self.mesh_cache: Dict[str, pv.PolyData] = {}
        self.available_meshes = [
            "sphere", "cube", "icosahedron", "torus", "cylinder",
            "cone", "dodecahedron", "octahedron", "tetrahedron",
            "pyramid", "disc", "ring", "helix", "mobius", "klein",
            "supertoroid", "star", "heart", "spiral", "fractal"
        ]
        
        # Mesh generation parameters
        self.default_params = MeshParameters()
        
        # Procedural mesh functions
        self.procedural_functions = {
            "star": self._create_star,
            "heart": self._create_heart,
            "spiral": self._create_spiral,
            "fractal": self._create_fractal,
            "flower": self._create_flower,
            "crystal": self._create_crystal,
            "wave": self._create_wave_surface,
            "mountains": self._create_mountains
        }
        
        # Initialize basic meshes
        self._initialize_basic_meshes()
    
    def _initialize_basic_meshes(self):
        """Pre-create commonly used meshes."""
        # Create and cache basic shapes
        self.meshes["sphere"] = self.create_sphere()
        self.meshes["cube"] = self.create_cube()
        self.meshes["icosahedron"] = self.create_icosahedron()
        self.meshes["torus"] = self.create_torus()
        self.meshes["cylinder"] = self.create_cylinder()
    
    def get_mesh(self, name: str) -> pv.PolyData:
        """Get a mesh by name, creating it if necessary."""
        if name in self.meshes:
            return self.meshes[name]
        
        # Try to create the mesh
        if name in self.mesh_cache:
            return self.mesh_cache[name]
        
        # Create mesh based on name
        mesh = self._create_mesh_by_name(name)
        if mesh:
            self.mesh_cache[name] = mesh
            return mesh
        
        # Default to sphere if not found
        print(f"Mesh '{name}' not found, returning sphere")
        return self.meshes["sphere"]
    
    def _create_mesh_by_name(self, name: str) -> Optional[pv.PolyData]:
        """Create a mesh based on its name."""
        creators = {
            "sphere": self.create_sphere,
            "cube": self.create_cube,
            "icosahedron": self.create_icosahedron,
            "torus": self.create_torus,
            "cylinder": self.create_cylinder,
            "cone": self.create_cone,
            "dodecahedron": self.create_dodecahedron,
            "octahedron": self.create_octahedron,
            "tetrahedron": self.create_tetrahedron,
            "pyramid": self.create_pyramid,
            "disc": self.create_disc,
            "ring": self.create_ring,
            "helix": self.create_helix,
            "mobius": self.create_mobius,
            "klein": self.create_klein_bottle,
            "supertoroid": self.create_supertoroid
        }
        
        if name in creators:
            return creators[name]()
        elif name in self.procedural_functions:
            return self.procedural_functions[name]()
        
        return None
    
    # === Basic Geometric Shapes ===
    
    def create_sphere(self, radius: float = 1.0, resolution: int = 50) -> pv.PolyData:
        """Create a sphere mesh."""
        return pv.Sphere(radius=radius, theta_resolution=resolution, phi_resolution=resolution)
    
    def create_cube(self, size: float = 2.0) -> pv.PolyData:
        """Create a cube mesh."""
        return pv.Cube(center=(0, 0, 0), x_length=size, y_length=size, z_length=size)
    
    def create_icosahedron(self, radius: float = 1.0) -> pv.PolyData:
        """Create an icosahedron mesh."""
        try:
            return pv.Icosahedron(radius=radius)
        except AttributeError:
            # Fallback to Icosphere or manual creation
            try:
                return pv.Icosphere(radius=radius, nsub=1)
            except AttributeError:
                # Create icosahedron manually
                phi = (1.0 + np.sqrt(5.0)) / 2.0
                vertices = np.array([
                    [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0],
                    [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi],
                    [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1]
                ]) * (radius / np.sqrt(phi * phi + 1))
                
                faces = np.array([
                    [3, 0, 11, 5], [3, 0, 5, 1], [3, 0, 1, 7], [3, 0, 7, 10], [3, 0, 10, 11],
                    [3, 1, 5, 9], [3, 5, 11, 4], [3, 11, 10, 2], [3, 10, 7, 6], [3, 7, 1, 8],
                    [3, 3, 9, 4], [3, 3, 4, 2], [3, 3, 2, 6], [3, 3, 6, 8], [3, 3, 8, 9],
                    [3, 4, 9, 5], [3, 2, 4, 11], [3, 6, 2, 10], [3, 8, 6, 7], [3, 9, 8, 1]
                ])
                
                return pv.PolyData(vertices, faces.ravel())
    
    def create_dodecahedron(self, radius: float = 1.0) -> pv.PolyData:
        """Create a dodecahedron mesh."""
        try:
            return pv.Dodecahedron(radius=radius)
        except AttributeError:
            # Fallback: use icosphere with more subdivisions
            try:
                return pv.Icosphere(radius=radius, nsub=2)
            except AttributeError:
                # Ultimate fallback to sphere
                return pv.Sphere(radius=radius, theta_resolution=20, phi_resolution=20)
    
    def create_octahedron(self, radius: float = 1.0) -> pv.PolyData:
        """Create an octahedron mesh."""
        try:
            return pv.Octahedron(radius=radius)
        except AttributeError:
            # Fallback: create manually
            vertices = np.array([
                [radius, 0, 0], [-radius, 0, 0],
                [0, radius, 0], [0, -radius, 0],
                [0, 0, radius], [0, 0, -radius]
            ])
            faces = np.array([
                [3, 0, 2, 4], [3, 0, 4, 3], [3, 0, 3, 5], [3, 0, 5, 2],
                [3, 1, 4, 2], [3, 1, 3, 4], [3, 1, 5, 3], [3, 1, 2, 5]
            ])
            return pv.PolyData(vertices, faces.ravel())
    
    def create_tetrahedron(self, radius: float = 1.0) -> pv.PolyData:
        """Create a tetrahedron mesh."""
        try:
            return pv.Tetrahedron(radius=radius)
        except AttributeError:
            # Create tetrahedron manually
            a = radius / np.sqrt(2)
            vertices = np.array([
                [a, a, a], [a, -a, -a],
                [-a, a, -a], [-a, -a, a]
            ])
            faces = np.array([
                [3, 0, 1, 2], [3, 0, 1, 3],
                [3, 0, 2, 3], [3, 1, 2, 3]
            ])
            return pv.PolyData(vertices, faces.ravel())
    
    def create_torus(self, r_major: float = 1.0, r_minor: float = 0.3) -> pv.PolyData:
        """Create a torus mesh."""
        # PyVista uses ParametricTorus
        try:
            return pv.ParametricTorus(ringradius=r_major, crosssectionradius=r_minor)
        except (AttributeError, TypeError):
            # Fallback: create torus manually using parametric equations
            u = np.linspace(0, 2 * np.pi, 50)
            v = np.linspace(0, 2 * np.pi, 50)
            u, v = np.meshgrid(u, v)
            
            x = (r_major + r_minor * np.cos(v)) * np.cos(u)
            y = (r_major + r_minor * np.cos(v)) * np.sin(u)
            z = r_minor * np.sin(v)
            
            grid = pv.StructuredGrid(x, y, z)
            return grid.extract_surface()
    
    def create_cylinder(self, radius: float = 0.5, height: float = 2.0, resolution: int = 30) -> pv.PolyData:
        """Create a cylinder mesh."""
        return pv.Cylinder(radius=radius, height=height, resolution=resolution)
    
    def create_cone(self, radius: float = 1.0, height: float = 2.0, resolution: int = 30) -> pv.PolyData:
        """Create a cone mesh."""
        return pv.Cone(radius=radius, height=height, resolution=resolution)
    
    def create_pyramid(self, base_size: float = 2.0, height: float = 2.0) -> pv.PolyData:
        """Create a pyramid mesh."""
        try:
            return pv.Pyramid(base_size=base_size, height=height)
        except AttributeError:
            # Create pyramid manually
            half = base_size / 2
            vertices = np.array([
                [-half, -half, 0], [half, -half, 0],
                [half, half, 0], [-half, half, 0],
                [0, 0, height]
            ])
            faces = np.array([
                [4, 0, 1, 2, 3],  # base
                [3, 0, 1, 4], [3, 1, 2, 4],
                [3, 2, 3, 4], [3, 3, 0, 4]
            ])
            return pv.PolyData(vertices, faces.ravel())
    
    def create_disc(self, inner: float = 0.0, outer: float = 1.0, resolution: int = 50) -> pv.PolyData:
        """Create a disc mesh."""
        return pv.Disc(inner=inner, outer=outer, r_res=resolution, c_res=resolution)
    
    def create_ring(self, inner: float = 0.5, outer: float = 1.0, height: float = 0.1) -> pv.PolyData:
        """Create a ring mesh."""
        disc = pv.Disc(inner=inner, outer=outer)
        return disc.extrude((0, 0, height))
    
    # === Advanced Geometric Shapes ===
    
    def create_helix(self, n_turns: int = 3, height: float = 2.0, radius: float = 1.0) -> pv.PolyData:
        """Create a helix mesh."""
        t = np.linspace(0, n_turns * 2 * np.pi, 100 * n_turns)
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = np.linspace(0, height, len(t))
        points = np.column_stack((x, y, z))
        
        # Create a tube along the helix path
        polyline = pv.PolyData()
        polyline.points = points
        cells = np.full((len(points) - 1, 3), 2)
        cells[:, 1] = np.arange(len(points) - 1)
        cells[:, 2] = np.arange(1, len(points))
        polyline.lines = cells.ravel()
        
        return polyline.tube(radius=0.05)
    
    def create_mobius(self, radius: float = 1.0, width: float = 0.3) -> pv.PolyData:
        """Create a Möbius strip."""
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(-width, width, 20)
        u, v = np.meshgrid(u, v)
        
        x = (radius + v * np.cos(u / 2)) * np.cos(u)
        y = (radius + v * np.cos(u / 2)) * np.sin(u)
        z = v * np.sin(u / 2)
        
        grid = pv.StructuredGrid(x, y, z)
        return grid.extract_surface()
    
    def create_klein_bottle(self, scale: float = 1.0) -> pv.PolyData:
        """Create a Klein bottle mesh."""
        u = np.linspace(0, 2 * np.pi, 50)
        v = np.linspace(0, 2 * np.pi, 50)
        u, v = np.meshgrid(u, v)
        
        a = 3.0 * scale
        x = (a + np.cos(u / 2) * np.sin(v) - np.sin(u / 2) * np.sin(2 * v)) * np.cos(u)
        y = (a + np.cos(u / 2) * np.sin(v) - np.sin(u / 2) * np.sin(2 * v)) * np.sin(u)
        z = np.sin(u / 2) * np.sin(v) + np.cos(u / 2) * np.sin(2 * v)
        
        grid = pv.StructuredGrid(x, y, z)
        return grid.extract_surface()
    
    def create_supertoroid(self, r_major: float = 1.0, r_minor: float = 0.3, n1: float = 2.0, n2: float = 2.0) -> pv.PolyData:
        """Create a supertoroid (generalized torus)."""
        u = np.linspace(-np.pi, np.pi, 50)
        v = np.linspace(-np.pi, np.pi, 50)
        u, v = np.meshgrid(u, v)
        
        def sign(x):
            return np.sign(x) * (np.abs(x) + 1e-10)
        
        cos_u = np.cos(u)
        sin_u = np.sin(u)
        cos_v = np.cos(v)
        sin_v = np.sin(v)
        
        x = (r_major + r_minor * sign(cos_v) * np.abs(cos_v) ** n2) * sign(cos_u) * np.abs(cos_u) ** n1
        y = (r_major + r_minor * sign(cos_v) * np.abs(cos_v) ** n2) * sign(sin_u) * np.abs(sin_u) ** n1
        z = r_minor * sign(sin_v) * np.abs(sin_v) ** n2
        
        grid = pv.StructuredGrid(x, y, z)
        return grid.extract_surface()
    
    # === Procedural Shapes ===
    
    def _create_star(self, n_points: int = 5, inner_radius: float = 0.5, outer_radius: float = 1.0) -> pv.PolyData:
        """Create a star-shaped mesh."""
        angles = np.linspace(0, 2 * np.pi, n_points * 2, endpoint=False)
        radii = np.array([outer_radius if i % 2 == 0 else inner_radius for i in range(n_points * 2)])
        
        x = radii * np.cos(angles)
        y = radii * np.sin(angles)
        z = np.zeros_like(x)
        
        points = np.column_stack((x, y, z))
        
        # Create polygon
        faces = [len(points)] + list(range(len(points)))
        mesh = pv.PolyData(points, faces=faces)
        
        # Extrude to give it depth
        return mesh.extrude((0, 0, 0.2))
    
    def _create_heart(self) -> pv.PolyData:
        """Create a heart-shaped mesh."""
        t = np.linspace(0, 2 * np.pi, 100)
        
        # Heart parametric equations
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
        z = np.zeros_like(x)
        
        # Normalize
        x = x / np.max(np.abs(x))
        y = y / np.max(np.abs(y))
        
        points = np.column_stack((x, y, z))
        
        # Create polygon and extrude
        faces = [len(points)] + list(range(len(points)))
        mesh = pv.PolyData(points, faces=faces)
        return mesh.extrude((0, 0, 0.3))
    
    def _create_spiral(self, n_turns: int = 5, growth_rate: float = 0.1) -> pv.PolyData:
        """Create a spiral mesh."""
        t = np.linspace(0, n_turns * 2 * np.pi, 200 * n_turns)
        radius = growth_rate * t
        
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = t / (2 * np.pi) * 0.1  # Slight vertical component
        
        points = np.column_stack((x, y, z))
        
        # Create polyline
        polyline = pv.PolyData()
        polyline.points = points
        cells = np.full((len(points) - 1, 3), 2)
        cells[:, 1] = np.arange(len(points) - 1)
        cells[:, 2] = np.arange(1, len(points))
        polyline.lines = cells.ravel()
        
        return polyline.tube(radius=0.02)
    
    def _create_fractal(self, iterations: int = 4, base_shape: str = "tetrahedron") -> pv.PolyData:
        """Create a simple fractal mesh (Sierpinski-like)."""
        if base_shape == "tetrahedron":
            mesh = self.create_tetrahedron()
        else:
            mesh = self.create_icosahedron()
        
        for i in range(iterations):
            # Subdivide
            mesh = mesh.subdivide(1)
            
            # Add noise for fractal appearance
            points = mesh.points
            noise = np.random.randn(*points.shape) * 0.01 * (0.5 ** i)
            mesh.points = points + noise
        
        return mesh
    
    def _create_flower(self, n_petals: int = 6, petal_width: float = 0.3) -> pv.PolyData:
        """Create a flower-shaped mesh."""
        theta = np.linspace(0, 2 * np.pi, 200)
        
        # Rose curve equation
        r = np.cos(n_petals * theta) + 0.5
        
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = np.sin(n_petals * theta) * 0.1  # Slight 3D effect
        
        points = np.column_stack((x, y, z))
        
        # Create surface
        faces = [len(points)] + list(range(len(points)))
        mesh = pv.PolyData(points, faces=faces)
        
        return mesh.extrude((0, 0, 0.2))
    
    def _create_crystal(self, n_sides: int = 6, height: float = 2.0) -> pv.PolyData:
        """Create a crystal-like mesh."""
        # Create base prism
        angles = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
        x_base = np.cos(angles)
        y_base = np.sin(angles)
        
        # Bottom points
        bottom_points = np.column_stack((x_base, y_base, np.zeros(n_sides)))
        
        # Middle points (wider)
        middle_points = np.column_stack((x_base * 1.2, y_base * 1.2, np.ones(n_sides) * height/2))
        
        # Top point
        top_point = np.array([[0, 0, height]])
        
        # Combine all points
        points = np.vstack([bottom_points, middle_points, top_point])
        
        # Create faces
        faces = []
        
        # Bottom face
        faces.append([n_sides] + list(range(n_sides)))
        
        # Side faces (bottom to middle)
        for i in range(n_sides):
            next_i = (i + 1) % n_sides
            faces.append([4, i, next_i, next_i + n_sides, i + n_sides])
        
        # Top faces (middle to apex)
        apex_idx = 2 * n_sides
        for i in range(n_sides):
            next_i = (i + 1) % n_sides
            faces.append([3, i + n_sides, next_i + n_sides, apex_idx])
        
        # Flatten faces list
        faces_flat = []
        for face in faces:
            faces_flat.extend(face)
        
        return pv.PolyData(points, faces=faces_flat)
    
    def _create_wave_surface(self, size: float = 5.0, frequency: float = 2.0, amplitude: float = 0.5) -> pv.PolyData:
        """Create a wave-like surface mesh."""
        x = np.linspace(-size/2, size/2, 50)
        y = np.linspace(-size/2, size/2, 50)
        x, y = np.meshgrid(x, y)
        
        # Wave equation
        r = np.sqrt(x**2 + y**2)
        z = amplitude * np.sin(frequency * r) / (r + 1)
        
        grid = pv.StructuredGrid(x, y, z)
        return grid.extract_surface()
    
    def _create_mountains(self, size: float = 5.0, roughness: float = 0.5) -> pv.PolyData:
        """Create a mountain-like terrain mesh."""
        # Create base grid
        x = np.linspace(-size/2, size/2, 100)
        y = np.linspace(-size/2, size/2, 100)
        x, y = np.meshgrid(x, y)
        
        # Generate height using multiple octaves of noise
        z = np.zeros_like(x)
        
        for octave in range(4):
            frequency = 2 ** octave
            amplitude = roughness ** octave
            
            # Simple noise function
            z += amplitude * (
                np.sin(frequency * x) * np.cos(frequency * y) +
                np.sin(frequency * 1.5 * x) * np.cos(frequency * 0.7 * y)
            )
        
        # Add central peak
        r = np.sqrt(x**2 + y**2)
        z += np.exp(-r**2 / 2) * 2
        
        grid = pv.StructuredGrid(x, y, z)
        return grid.extract_surface()
    
    # === Mesh Operations ===
    
    def morph_meshes(self, mesh1: pv.PolyData, mesh2: pv.PolyData, factor: float) -> pv.PolyData:
        """Morph between two meshes."""
        # Ensure meshes have same number of points
        if mesh1.n_points != mesh2.n_points:
            # Resample mesh2 to match mesh1
            mesh2 = self._resample_mesh(mesh2, mesh1.n_points)
        
        # Interpolate points
        morphed_points = mesh1.points * (1 - factor) + mesh2.points * factor
        
        # Create new mesh with morphed points
        morphed = mesh1.copy()
        morphed.points = morphed_points
        
        return morphed
    
    def _resample_mesh(self, mesh: pv.PolyData, n_points: int) -> pv.PolyData:
        """Resample a mesh to have a specific number of points."""
        # Simple resampling - subdivide or decimate as needed
        current_points = mesh.n_points
        
        if current_points < n_points:
            # Subdivide
            subdivisions = int(np.log2(n_points / current_points)) + 1
            mesh = mesh.subdivide(subdivisions)
        
        # Decimate to exact number
        if mesh.n_points != n_points:
            target_reduction = 1.0 - (n_points / mesh.n_points)
            if target_reduction > 0:
                mesh = mesh.decimate(target_reduction)
        
        return mesh
    
    def apply_noise(self, mesh: pv.PolyData, amplitude: float = 0.1) -> pv.PolyData:
        """Apply noise to mesh vertices."""
        noisy_mesh = mesh.copy()
        noise = np.random.randn(*mesh.points.shape) * amplitude
        noisy_mesh.points = mesh.points + noise
        return noisy_mesh
    
    def apply_twist(self, mesh: pv.PolyData, angle: float = np.pi) -> pv.PolyData:
        """Apply a twist deformation to a mesh."""
        twisted = mesh.copy()
        points = mesh.points.copy()
        
        # Twist around z-axis
        z_range = points[:, 2].max() - points[:, 2].min()
        if z_range > 0:
            twist_factor = (points[:, 2] - points[:, 2].min()) / z_range * angle
            
            cos_twist = np.cos(twist_factor)
            sin_twist = np.sin(twist_factor)
            
            new_x = points[:, 0] * cos_twist - points[:, 1] * sin_twist
            new_y = points[:, 0] * sin_twist + points[:, 1] * cos_twist
            
            twisted.points[:, 0] = new_x
            twisted.points[:, 1] = new_y
        
        return twisted
    
    def get_mesh_info(self, name: str) -> Dict:
        """Get information about a mesh."""
        mesh = self.get_mesh(name)
        return {
            "name": name,
            "n_points": mesh.n_points,
            "n_cells": mesh.n_cells,
            "bounds": mesh.bounds,
            "center": mesh.center,
            "volume": mesh.volume if hasattr(mesh, 'volume') else None,
            "area": mesh.area if hasattr(mesh, 'area') else None
        }


# Test function
def test_mesh_manager():
    """Test mesh manager functionality."""
    print("Testing Mesh Manager")
    print("=" * 50)
    
    manager = MeshManager()
    
    # Test basic shapes
    print("\n✓ Basic shapes available:")
    for shape in ["sphere", "cube", "torus", "cylinder", "cone"]:
        mesh = manager.get_mesh(shape)
        print(f"  • {shape}: {mesh.n_points} points, {mesh.n_cells} cells")
    
    # Test advanced shapes
    print("\n✓ Advanced shapes available:")
    for shape in ["helix", "mobius", "klein", "supertoroid"]:
        mesh = manager.get_mesh(shape)
        print(f"  • {shape}: {mesh.n_points} points, {mesh.n_cells} cells")
    
    # Test procedural shapes
    print("\n✓ Procedural shapes available:")
    for shape in ["star", "heart", "spiral", "flower", "crystal"]:
        mesh = manager.get_mesh(shape)
        print(f"  • {shape}: {mesh.n_points} points, {mesh.n_cells} cells")
    
    # Test mesh operations
    sphere = manager.get_mesh("sphere")
    cube = manager.get_mesh("cube")
    morphed = manager.morph_meshes(sphere, cube, 0.5)
    print(f"\n✓ Morphed mesh (50% sphere-cube): {morphed.n_points} points")
    
    # Test deformations
    twisted_cylinder = manager.apply_twist(manager.get_mesh("cylinder"))
    print(f"✓ Twisted cylinder: {twisted_cylinder.n_points} points")
    
    noisy_sphere = manager.apply_noise(sphere, 0.05)
    print(f"✓ Noisy sphere: {noisy_sphere.n_points} points")
    
    print("\n✅ All mesh manager tests passed!")


if __name__ == "__main__":
    test_mesh_manager()
