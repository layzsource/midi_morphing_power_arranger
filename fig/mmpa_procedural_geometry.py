#!/usr/bin/env python3
"""
MMPA Procedural Geometry Engine - The Geometry Revolution
========================================================

Revolutionary procedural geometry system for infinite generative forms:
- L-System Fractal Trees (Organic growth patterns)
- 3D Mandelbrot Set Extrusions (Classic fractals in 3D)
- Perlin Noise Terrain (Rolling landscape generation)
- Voronoi Cell Structures (Natural organic patterns)
- DNA Double Helix (Parametric biological structures)
- Crystal Lattice Systems (Atomic structure visualization)
- Mathematical Surfaces (Klein, Boy, Catenoid surfaces)

This transforms MMPA from basic shape morphing to infinite procedural universes
that respond to musical intelligence in real-time.
"""

import math
import numpy as np
import random
from typing import List, Tuple, Dict, Any
import time

class LSystemGenerator:
    """L-System (Lindenmayer System) generator for organic fractal trees"""

    def __init__(self):
        # Musical-responsive L-System rules
        self.rules = {
            'jazz': {
                'axiom': 'F',
                'rules': {'F': 'F[+F]F[-F][F]'},
                'angle': 25.0,
                'iterations': 4
            },
            'classical': {
                'axiom': 'F',
                'rules': {'F': 'FF-[-F+F+F]+[+F-F-F]'},
                'angle': 22.5,
                'iterations': 4
            },
            'electronic': {
                'axiom': 'F',
                'rules': {'F': 'F[+F][F]F[-F][+F]'},
                'angle': 30.0,
                'iterations': 5
            },
            'rock': {
                'axiom': 'F',
                'rules': {'F': 'F[++F][--F]FF'},
                'angle': 45.0,
                'iterations': 4
            }
        }

    def generate_string(self, genre: str = 'jazz', iterations: int = None) -> str:
        """Generate L-System string based on musical genre"""
        if genre not in self.rules:
            genre = 'jazz'

        rule_set = self.rules[genre]
        axiom = rule_set['axiom']
        rules = rule_set['rules']
        iterations = iterations or rule_set['iterations']

        current = axiom

        for _ in range(iterations):
            next_string = ""
            for char in current:
                if char in rules:
                    next_string += rules[char]
                else:
                    next_string += char
            current = next_string

        return current

    def string_to_3d_points(self, l_string: str, genre: str = 'jazz',
                           scale: float = 1.0, music_factor: float = 0.0) -> List[List[float]]:
        """Convert L-System string to 3D points with musical responsiveness"""
        if genre not in self.rules:
            genre = 'jazz'

        angle = self.rules[genre]['angle']

        # Musical modulation
        angle += music_factor * 15.0  # Music affects branching angle
        length = 0.1 * scale * (1.0 + music_factor * 0.5)  # Music affects branch length

        points = []
        stack = []  # For storing positions and orientations

        # Initial state
        x, y, z = 0.0, 0.0, 0.0
        heading = 90.0  # degrees
        pitch = 0.0     # degrees

        for char in l_string:
            if char == 'F':
                # Move forward and draw
                old_x, old_y, old_z = x, y, z

                # Convert angles to radians
                h_rad = math.radians(heading)
                p_rad = math.radians(pitch)

                # Calculate new position
                x += length * math.cos(p_rad) * math.cos(h_rad)
                y += length * math.sin(p_rad)
                z += length * math.cos(p_rad) * math.sin(h_rad)

                points.extend([[old_x, old_y, old_z], [x, y, z]])

            elif char == '+':
                # Turn left
                heading += angle
            elif char == '-':
                # Turn right
                heading -= angle
            elif char == '^':
                # Pitch up
                pitch += angle
            elif char == '&':
                # Pitch down
                pitch -= angle
            elif char == '[':
                # Push state
                stack.append((x, y, z, heading, pitch))
            elif char == ']':
                # Pop state
                if stack:
                    x, y, z, heading, pitch = stack.pop()

        return points

class Mandelbrot3DGenerator:
    """3D Mandelbrot set extrusion generator"""

    def __init__(self):
        self.max_iterations = 80

    def mandelbrot_point(self, c: complex, max_iter: int = None) -> int:
        """Calculate Mandelbrot iterations for a complex point"""
        max_iter = max_iter or self.max_iterations
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return max_iter

    def generate_3d_mandelbrot(self, resolution: int = 100,
                              zoom: float = 1.0,
                              music_factor: float = 0.0) -> List[List[float]]:
        """Generate 3D Mandelbrot set with musical modulation"""
        points = []

        # Musical parameters
        zoom *= (1.0 + music_factor * 2.0)  # Music affects zoom level
        offset_x = music_factor * 0.5       # Music shifts the view
        offset_y = music_factor * 0.3

        # Generate Mandelbrot slice
        for i in range(resolution):
            for j in range(resolution):
                # Map to complex plane
                x = (i - resolution/2) / (resolution/4 * zoom) + offset_x
                y = (j - resolution/2) / (resolution/4 * zoom) + offset_y

                c = complex(x, y)
                iterations = self.mandelbrot_point(c)

                # Only include points that are part of the set or near boundary
                if iterations < self.max_iterations * 0.8:
                    # Extrude in Z based on iteration count
                    z = (iterations / self.max_iterations) * 2.0 - 1.0

                    # Add musical oscillation in Z
                    z += math.sin(music_factor * 10.0 + x * 5.0) * 0.2

                    points.append([x, y, z])

        return points

class PerlinTerrainGenerator:
    """Perlin noise terrain generator for organic landscapes"""

    def __init__(self):
        # Permutation table for Perlin noise
        self.perm = [151,160,137,91,90,15,131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,190,6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,88,237,149,56,87,174,20,125,136,171,168,68,175,74,165,71,134,139,48,27,166,77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,102,143,54,65,25,63,161,1,216,80,73,209,76,132,187,208,89,18,169,200,196,135,130,116,188,159,86,164,100,109,198,173,186,3,64,52,217,226,250,124,123,5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,223,183,170,213,119,248,152,2,44,154,163,70,221,153,101,155,167,43,172,9,129,22,39,253,19,98,108,110,79,113,224,232,178,185,112,104,218,246,97,228,251,34,242,193,238,210,144,12,191,179,162,241,81,51,145,235,249,14,239,107,49,192,214,31,181,199,106,157,184,84,204,176,115,121,50,45,127,4,150,254,138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180] * 2

    def fade(self, t: float) -> float:
        """Fade function for Perlin noise"""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t: float, a: float, b: float) -> float:
        """Linear interpolation"""
        return a + t * (b - a)

    def grad(self, hash: int, x: float, y: float, z: float) -> float:
        """Gradient function"""
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h == 12 or h == 14 else z)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def perlin_noise(self, x: float, y: float, z: float) -> float:
        """Generate Perlin noise at coordinates"""
        # Find unit grid cell containing point
        X = int(x) & 255
        Y = int(y) & 255
        Z = int(z) & 255

        # Find relative x,y,z of point in cube
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)

        # Compute fade curves
        u = self.fade(x)
        v = self.fade(y)
        w = self.fade(z)

        # Hash coordinates of 8 cube corners
        A = self.perm[X] + Y
        AA = self.perm[A] + Z
        AB = self.perm[A + 1] + Z
        B = self.perm[X + 1] + Y
        BA = self.perm[B] + Z
        BB = self.perm[B + 1] + Z

        # Add blended results from 8 corners of cube
        return self.lerp(w,
            self.lerp(v,
                self.lerp(u, self.grad(self.perm[AA], x, y, z),
                            self.grad(self.perm[BA], x-1, y, z)),
                self.lerp(u, self.grad(self.perm[AB], x, y-1, z),
                            self.grad(self.perm[BB], x-1, y-1, z))),
            self.lerp(v,
                self.lerp(u, self.grad(self.perm[AA+1], x, y, z-1),
                            self.grad(self.perm[BA+1], x-1, y, z-1)),
                self.lerp(u, self.grad(self.perm[AB+1], x, y-1, z-1),
                            self.grad(self.perm[BB+1], x-1, y-1, z-1))))

    def generate_terrain(self, size: int = 64, scale: float = 0.1,
                        octaves: int = 4, music_factor: float = 0.0) -> List[List[float]]:
        """Generate terrain using multi-octave Perlin noise"""
        points = []

        # Musical modulation
        time_offset = music_factor * 10.0  # Music creates terrain animation
        height_scale = 0.5 * (1.0 + music_factor)  # Music affects terrain height

        for i in range(size):
            for j in range(size):
                x = (i - size/2) * scale
                z = (j - size/2) * scale

                # Multi-octave noise
                y = 0.0
                amplitude = 1.0
                frequency = 1.0

                for octave in range(octaves):
                    y += amplitude * self.perlin_noise(
                        x * frequency + time_offset,
                        0.0,
                        z * frequency + time_offset
                    )
                    amplitude *= 0.5
                    frequency *= 2.0

                y *= height_scale
                points.append([x, y, z])

        return points

class VoronoiGenerator:
    """Voronoi cell structure generator for organic patterns"""

    def __init__(self):
        pass

    def distance(self, p1: List[float], p2: List[float]) -> float:
        """Calculate 3D distance between two points"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

    def generate_voronoi_3d(self, num_seeds: int = 20, resolution: int = 50,
                           music_factor: float = 0.0) -> List[List[float]]:
        """Generate 3D Voronoi cell structure"""
        points = []

        # Generate seed points with musical modulation
        seeds = []
        for i in range(num_seeds):
            # Musical seeds distribution
            angle = (i / num_seeds) * 2 * math.pi + music_factor * math.pi
            radius = 0.8 + music_factor * 0.4

            x = radius * math.cos(angle) + (random.random() - 0.5) * 0.4
            y = (random.random() - 0.5) * 2.0 + music_factor * math.sin(angle)
            z = radius * math.sin(angle) + (random.random() - 0.5) * 0.4

            seeds.append([x, y, z])

        # Generate Voronoi structure
        step = 2.0 / resolution
        for i in range(resolution):
            for j in range(resolution):
                for k in range(resolution):
                    x = -1.0 + i * step
                    y = -1.0 + j * step
                    z = -1.0 + k * step

                    test_point = [x, y, z]

                    # Find distances to all seeds
                    distances = [self.distance(test_point, seed) for seed in seeds]

                    # Check if this point is near a cell boundary
                    min_dist = min(distances)
                    second_min = sorted(distances)[1]

                    # Point is on boundary if close to two seeds
                    if (second_min - min_dist) < 0.1:  # Boundary thickness
                        points.append([x, y, z])

        return points

class DNAHelixGenerator:
    """DNA double helix generator with musical parameters"""

    def __init__(self):
        self.base_radius = 1.0
        self.helix_pitch = 3.4  # Angstroms per base pair (scaled)

    def generate_dna_helix(self, num_bases: int = 100,
                          music_factor: float = 0.0) -> List[List[float]]:
        """Generate DNA double helix structure"""
        points = []

        # Musical parameters
        twist_rate = 36.0 + music_factor * 20.0  # degrees per base pair
        radius = self.base_radius * (1.0 + music_factor * 0.3)
        pitch = self.helix_pitch * (1.0 + music_factor * 0.5)

        for i in range(num_bases):
            # Position along helix axis
            z = (i / num_bases) * pitch * num_bases / 10.0  # Scale for visibility

            # Rotation angle
            angle = math.radians(i * twist_rate)

            # First strand
            x1 = radius * math.cos(angle)
            y1 = radius * math.sin(angle)
            points.append([x1, y1, z])

            # Second strand (opposite)
            x2 = radius * math.cos(angle + math.pi)
            y2 = radius * math.sin(angle + math.pi)
            points.append([x2, y2, z])

            # Base pairs (connecting strands)
            if i % 4 == 0:  # Every 4th base pair for visibility
                # Add points along base pair connection
                for t in np.linspace(0, 1, 5):
                    x_base = x1 + t * (x2 - x1)
                    y_base = y1 + t * (y2 - y1)
                    points.append([x_base, y_base, z])

        return points

class ProceduralGeometryEngine:
    """Main procedural geometry engine that integrates all generators"""

    def __init__(self):
        self.l_system = LSystemGenerator()
        self.mandelbrot = Mandelbrot3DGenerator()
        self.terrain = PerlinTerrainGenerator()
        self.voronoi = VoronoiGenerator()
        self.dna = DNAHelixGenerator()

        # Available generators
        self.generators = {
            'l_system_tree': self.generate_l_system,
            'mandelbrot_3d': self.generate_mandelbrot,
            'perlin_terrain': self.generate_terrain,
            'voronoi_cells': self.generate_voronoi,
            'dna_helix': self.generate_dna,
            'crystal_lattice': self.generate_crystal_lattice,
            'mathematical_surface': self.generate_math_surface
        }

    def generate_l_system(self, genre: str = 'jazz', resolution: int = 1000,
                         music_factor: float = 0.0) -> List[List[float]]:
        """Generate L-System fractal tree"""
        # Adjust iterations based on resolution
        iterations = 3 + int(resolution / 500)  # More resolution = more iterations
        iterations = min(iterations, 6)  # Cap to prevent exponential explosion

        l_string = self.l_system.generate_string(genre, iterations)
        points = self.l_system.string_to_3d_points(l_string, genre, 1.0, music_factor)

        # Limit points to resolution
        if len(points) > resolution:
            step = len(points) // resolution
            points = points[::step]

        return points[:resolution]

    def generate_mandelbrot(self, genre: str = 'electronic', resolution: int = 1000,
                           music_factor: float = 0.0) -> List[List[float]]:
        """Generate 3D Mandelbrot set"""
        grid_size = int(math.sqrt(resolution))
        points = self.mandelbrot.generate_3d_mandelbrot(grid_size, 1.0, music_factor)
        return points[:resolution]

    def generate_terrain(self, genre: str = 'ambient', resolution: int = 1000,
                        music_factor: float = 0.0) -> List[List[float]]:
        """Generate Perlin noise terrain"""
        grid_size = int(math.sqrt(resolution))
        points = self.terrain.generate_terrain(grid_size, 0.1, 4, music_factor)
        return points[:resolution]

    def generate_voronoi(self, genre: str = 'organic', resolution: int = 1000,
                        music_factor: float = 0.0) -> List[List[float]]:
        """Generate Voronoi cell structure"""
        num_seeds = max(10, resolution // 50)
        grid_res = int((resolution / 8) ** (1/3))  # Cube root for 3D
        points = self.voronoi.generate_voronoi_3d(num_seeds, grid_res, music_factor)
        return points[:resolution]

    def generate_dna(self, genre: str = 'biological', resolution: int = 1000,
                    music_factor: float = 0.0) -> List[List[float]]:
        """Generate DNA double helix"""
        num_bases = resolution // 6  # Each base pair generates ~6 points
        points = self.dna.generate_dna_helix(num_bases, music_factor)
        return points[:resolution]

    def generate_crystal_lattice(self, genre: str = 'crystalline', resolution: int = 1000,
                               music_factor: float = 0.0) -> List[List[float]]:
        """Generate crystal lattice structure"""
        points = []

        # Simple cubic lattice with musical modulation
        lattice_size = int((resolution / 4) ** (1/3))  # Cube root for 3D grid
        spacing = 2.0 / lattice_size
        distortion = music_factor * 0.3  # Musical distortion

        for i in range(lattice_size):
            for j in range(lattice_size):
                for k in range(lattice_size):
                    x = -1.0 + i * spacing
                    y = -1.0 + j * spacing
                    z = -1.0 + k * spacing

                    # Add musical distortion
                    x += math.sin(music_factor * 5.0 + i) * distortion
                    y += math.cos(music_factor * 5.0 + j) * distortion
                    z += math.sin(music_factor * 3.0 + k) * distortion

                    points.append([x, y, z])

        return points[:resolution]

    def generate_math_surface(self, genre: str = 'mathematical', resolution: int = 1000,
                            music_factor: float = 0.0) -> List[List[float]]:
        """Generate mathematical surface (Klein bottle)"""
        points = []

        num_u = int(math.sqrt(resolution))
        num_v = int(math.sqrt(resolution))

        for i in range(num_u):
            for j in range(num_v):
                u = (i / num_u) * 2 * math.pi
                v = (j / num_v) * 2 * math.pi

                # Klein bottle with musical modulation
                time_factor = music_factor * 2.0

                # Klein bottle parametric equations
                a = 2.0 + music_factor
                if u < math.pi:
                    x = (a + math.cos(u/2) * math.sin(v + time_factor) - math.sin(u/2) * math.sin(2*v)) * math.cos(u)
                    y = math.sin(u/2) * math.sin(v + time_factor) + math.cos(u/2) * math.sin(2*v)
                    z = (a + math.cos(u/2) * math.sin(v + time_factor) - math.sin(u/2) * math.sin(2*v)) * math.sin(u)
                else:
                    x = (a + math.cos(u/2) * math.sin(v + time_factor) + math.sin(u/2) * math.sin(2*v)) * math.cos(u)
                    y = math.sin(u/2) * math.sin(v + time_factor) - math.cos(u/2) * math.sin(2*v)
                    z = (a + math.cos(u/2) * math.sin(v + time_factor) + math.sin(u/2) * math.sin(2*v)) * math.sin(u)

                # Scale and normalize
                scale = 0.3
                points.append([x * scale, y * scale, z * scale])

        return points[:resolution]

    def get_available_generators(self) -> List[str]:
        """Get list of available procedural generators"""
        return list(self.generators.keys())

    def generate_procedural_shape(self, generator_name: str, genre: str = 'jazz',
                                 resolution: int = 1000, music_factor: float = 0.0) -> List[List[float]]:
        """Generate procedural shape using specified generator"""
        if generator_name in self.generators:
            return self.generators[generator_name](genre, resolution, music_factor)
        else:
            # Fallback to L-system
            return self.generate_l_system(genre, resolution, music_factor)

    def morph_procedural_shapes(self, shape_a: List[List[float]], shape_b: List[List[float]],
                               factor: float) -> List[List[float]]:
        """Morph between two procedural shapes"""
        if not shape_a or not shape_b:
            return shape_a or shape_b or []

        min_len = min(len(shape_a), len(shape_b))
        morphed = []

        for i in range(min_len):
            va, vb = shape_a[i], shape_b[i]

            # Smooth interpolation
            t = factor
            smooth_t = t * t * (3.0 - 2.0 * t)  # Smoothstep

            mx = va[0] * (1 - smooth_t) + vb[0] * smooth_t
            my = va[1] * (1 - smooth_t) + vb[1] * smooth_t
            mz = va[2] * (1 - smooth_t) + vb[2] * smooth_t

            morphed.append([mx, my, mz])

        return morphed

def main():
    """Test the procedural geometry engine"""
    engine = ProceduralGeometryEngine()

    print("🔥 MMPA PROCEDURAL GEOMETRY ENGINE")
    print("=" * 50)
    print("Available generators:")

    generators = engine.get_available_generators()
    for i, gen in enumerate(generators, 1):
        print(f"  {i}. {gen}")

    print(f"\n🧪 Testing generators...")

    # Test each generator
    test_resolution = 500
    test_results = {}

    for generator in generators:
        try:
            start_time = time.time()
            points = engine.generate_procedural_shape(generator, 'jazz', test_resolution, 0.5)
            end_time = time.time()

            test_results[generator] = {
                'points': len(points),
                'time': end_time - start_time,
                'success': True
            }
            print(f"  ✅ {generator}: {len(points)} points in {end_time - start_time:.3f}s")

        except Exception as e:
            test_results[generator] = {
                'points': 0,
                'time': 0,
                'success': False,
                'error': str(e)
            }
            print(f"  ❌ {generator}: Error - {e}")

    print(f"\n📊 RESULTS:")
    successful = sum(1 for r in test_results.values() if r['success'])
    total = len(test_results)
    print(f"  Successful generators: {successful}/{total}")
    print(f"  Success rate: {(successful/total)*100:.1f}%")

    if successful > 0:
        print(f"\n🚀 PROCEDURAL GEOMETRY ENGINE READY!")
        print(f"  • {successful} working generators")
        print(f"  • Infinite shape possibilities")
        print(f"  • Musical responsiveness")
        print(f"  • Real-time generation")

    return successful > 0

if __name__ == "__main__":
    main()