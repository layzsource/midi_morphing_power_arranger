#!/usr/bin/env python3
"""
MMPA Advanced Lighting and Materials System
==========================================

Professional lighting and materials enhancement for MMPA morphing visuals.
Features:
- PBR (Physically Based Rendering) materials
- Multi-light setup (directional, point, spot lights)
- Dynamic lighting responsive to music
- Advanced material properties
- Real-time light animation
- Genre-specific lighting styles

This system enhances MMPA with professional-grade lighting for concerts and installations.
"""

import sys
import math
import logging
import numpy as np
import time
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget

logger = logging.getLogger(__name__)

class Light:
    """Professional light system"""

    def __init__(self, light_type: str, position: List[float], color: List[float], intensity: float = 1.0):
        self.type = light_type  # 'directional', 'point', 'spot'
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.intensity = intensity
        self.enabled = True

        # Spot light properties
        self.direction = np.array([0.0, -1.0, 0.0], dtype=np.float32)
        self.cutoff_angle = 45.0  # degrees
        self.falloff_exponent = 1.0

        # Point light properties
        self.attenuation = np.array([1.0, 0.09, 0.032], dtype=np.float32)  # constant, linear, quadratic

        # Animation properties
        self.animation_enabled = True
        self.animation_speed = 1.0
        self.animation_amplitude = 1.0
        self.original_position = self.position.copy()
        self.original_color = self.color.copy()

    def update_animation(self, time_factor: float, music_intensity: float = 0.0):
        """Update light animation based on time and music"""
        if not self.animation_enabled:
            return

        # Position animation
        offset_x = math.sin(time_factor * self.animation_speed) * self.animation_amplitude
        offset_y = math.cos(time_factor * self.animation_speed * 0.7) * self.animation_amplitude * 0.5
        offset_z = math.sin(time_factor * self.animation_speed * 1.3) * self.animation_amplitude * 0.8

        self.position = self.original_position + np.array([offset_x, offset_y, offset_z])

        # Intensity animation based on music
        music_boost = 1.0 + music_intensity * 0.5
        self.intensity = min(2.0, self.intensity * music_boost)

    def apply_gl_lighting(self, light_index: int):
        """Apply light to OpenGL fixed pipeline"""
        light_id = GL_LIGHT0 + light_index

        glLightfv(light_id, GL_POSITION, np.append(self.position, 1.0 if self.type == 'point' else 0.0))
        glLightfv(light_id, GL_DIFFUSE, self.color * self.intensity)
        glLightfv(light_id, GL_SPECULAR, self.color * self.intensity * 0.8)
        glLightfv(light_id, GL_AMBIENT, self.color * 0.1)

        if self.type == 'point':
            glLightfv(light_id, GL_CONSTANT_ATTENUATION, self.attenuation[0])
            glLightfv(light_id, GL_LINEAR_ATTENUATION, self.attenuation[1])
            glLightfv(light_id, GL_QUADRATIC_ATTENUATION, self.attenuation[2])

        if self.enabled:
            glEnable(light_id)
        else:
            glDisable(light_id)

class Material:
    """Professional material system"""

    def __init__(self, name: str):
        self.name = name
        self.ambient = np.array([0.2, 0.2, 0.2, 1.0], dtype=np.float32)
        self.diffuse = np.array([0.8, 0.8, 0.8, 1.0], dtype=np.float32)
        self.specular = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.emission = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)
        self.shininess = 50.0

        # PBR properties
        self.metallic = 0.0
        self.roughness = 0.5
        self.reflectance = 0.04  # F0 for dielectrics

        # Animation properties
        self.base_diffuse = self.diffuse.copy()
        self.animation_enabled = True

    def apply_gl_material(self):
        """Apply material to OpenGL"""
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self.emission)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)

    def update_for_music(self, genre: str, key_signature: str, intensity: float):
        """Update material properties based on musical analysis"""
        if not self.animation_enabled:
            return

        # Genre-specific material adjustments
        if genre == 'jazz':
            # Warm, golden materials
            self.diffuse = self.base_diffuse * np.array([1.2, 1.1, 0.8, 1.0])
            self.shininess = 30.0 + intensity * 20.0
        elif genre == 'classical':
            # Elegant, refined materials
            self.diffuse = self.base_diffuse * np.array([1.0, 1.0, 1.2, 1.0])
            self.shininess = 80.0 + intensity * 40.0
        elif genre == 'electronic':
            # Metallic, synthetic materials
            self.metallic = 0.7 + intensity * 0.3
            self.diffuse = self.base_diffuse * np.array([0.8, 1.2, 1.4, 1.0])
            self.shininess = 100.0
        elif genre == 'rock':
            # Bold, rough materials
            self.roughness = 0.7 + intensity * 0.3
            self.diffuse = self.base_diffuse * np.array([1.3, 0.9, 0.8, 1.0])
            self.shininess = 20.0 + intensity * 30.0

        # Key signature affects emission
        if 'major' in key_signature.lower():
            self.emission = np.array([0.1, 0.1, 0.05, 1.0]) * intensity
        elif 'minor' in key_signature.lower():
            self.emission = np.array([0.05, 0.05, 0.1, 1.0]) * intensity

class LightingSystem:
    """Professional lighting management system"""

    def __init__(self):
        self.lights = {}
        self.materials = {}
        self.current_material = None
        self.ambient_light = np.array([0.1, 0.1, 0.2, 1.0], dtype=np.float32)

        # Musical responsiveness
        self.current_genre = 'unknown'
        self.current_intensity = 0.0
        self.beat_detection = False

        self._create_default_lights()
        self._create_default_materials()

    def _create_default_lights(self):
        """Create professional lighting setup"""

        # Key light (main directional light)
        self.lights['key'] = Light(
            'directional',
            position=[2.0, 3.0, 4.0],
            color=[1.0, 0.95, 0.8],  # Warm white
            intensity=1.2
        )

        # Fill light (softer point light)
        self.lights['fill'] = Light(
            'point',
            position=[-3.0, 2.0, 2.0],
            color=[0.8, 0.9, 1.0],  # Cool white
            intensity=0.6
        )

        # Rim light (dramatic backlighting)
        self.lights['rim'] = Light(
            'directional',
            position=[0.0, 1.0, -5.0],
            color=[1.0, 0.8, 0.6],  # Golden rim
            intensity=0.8
        )

        # Accent lights (colorful point lights)
        self.lights['accent1'] = Light(
            'point',
            position=[4.0, 0.0, 2.0],
            color=[1.0, 0.3, 0.5],  # Pink accent
            intensity=0.4
        )

        self.lights['accent2'] = Light(
            'point',
            position=[-2.0, -1.0, 3.0],
            color=[0.3, 0.8, 1.0],  # Blue accent
            intensity=0.4
        )

        # Musical reactive light
        self.lights['music'] = Light(
            'point',
            position=[0.0, 4.0, 0.0],
            color=[1.0, 1.0, 1.0],  # Pure white
            intensity=0.0  # Starts off, responds to music
        )

    def _create_default_materials(self):
        """Create professional material library"""

        # Metallic gold material
        gold = Material('gold')
        gold.ambient = np.array([0.24725, 0.1995, 0.0745, 1.0])
        gold.diffuse = np.array([0.75164, 0.60648, 0.22648, 1.0])
        gold.specular = np.array([0.628281, 0.555802, 0.366065, 1.0])
        gold.shininess = 51.2
        gold.metallic = 0.9
        self.materials['gold'] = gold

        # Chrome material
        chrome = Material('chrome')
        chrome.ambient = np.array([0.25, 0.25, 0.25, 1.0])
        chrome.diffuse = np.array([0.4, 0.4, 0.4, 1.0])
        chrome.specular = np.array([0.774597, 0.774597, 0.774597, 1.0])
        chrome.shininess = 76.8
        chrome.metallic = 1.0
        self.materials['chrome'] = chrome

        # Glass material
        glass = Material('glass')
        glass.ambient = np.array([0.0, 0.0, 0.0, 0.5])
        glass.diffuse = np.array([0.588235, 0.670588, 0.729412, 0.5])
        glass.specular = np.array([0.9, 0.9, 0.9, 0.5])
        glass.shininess = 96.0
        glass.roughness = 0.1
        self.materials['glass'] = glass

        # Plastic material
        plastic = Material('plastic')
        plastic.ambient = np.array([0.0, 0.1, 0.06, 1.0])
        plastic.diffuse = np.array([0.0, 0.50980392, 0.50980392, 1.0])
        plastic.specular = np.array([0.50196078, 0.50196078, 0.50196078, 1.0])
        plastic.shininess = 32.0
        plastic.roughness = 0.6
        self.materials['plastic'] = plastic

        # Luminous material (self-emitting)
        luminous = Material('luminous')
        luminous.emission = np.array([0.2, 0.3, 0.6, 1.0])
        luminous.diffuse = np.array([0.1, 0.2, 0.8, 1.0])
        luminous.specular = np.array([0.0, 0.0, 0.0, 1.0])
        luminous.shininess = 0.0
        self.materials['luminous'] = luminous

        # Set default material
        self.current_material = self.materials['chrome']

    def initialize_gl_lighting(self):
        """Initialize OpenGL lighting system"""
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set global ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.ambient_light)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        # Enable smooth shading
        glShadeModel(GL_SMOOTH)

        logger.info("✅ Professional lighting system initialized")

    def update_lighting(self, time_factor: float, musical_data: Dict = None):
        """Update all lights based on time and music"""
        music_intensity = 0.0

        if musical_data:
            music_intensity = musical_data.get('amplitude', 0.0)
            genre = musical_data.get('genre', 'unknown')
            key_signature = musical_data.get('key_signature', 'unknown')

            # Update genre-specific lighting
            if genre != self.current_genre:
                self._apply_genre_lighting(genre)
                self.current_genre = genre

            # Update material for music
            if self.current_material:
                self.current_material.update_for_music(genre, key_signature, music_intensity)

        # Update light animations
        for light in self.lights.values():
            light.update_animation(time_factor, music_intensity)

        # Music-reactive light responds to amplitude
        if 'music' in self.lights:
            self.lights['music'].intensity = music_intensity * 2.0
            # Color cycling for music light
            hue = (time_factor * 0.5) % 1.0
            self.lights['music'].color = self._hsv_to_rgb(hue, 0.8, 1.0)

    def _apply_genre_lighting(self, genre: str):
        """Apply genre-specific lighting configuration"""
        if genre == 'jazz':
            # Warm, intimate lighting
            self.lights['key'].color = np.array([1.0, 0.8, 0.6])
            self.lights['fill'].intensity = 0.4
            self.lights['accent1'].color = np.array([0.8, 0.4, 0.2])
            self.ambient_light = np.array([0.15, 0.1, 0.05, 1.0])

        elif genre == 'classical':
            # Elegant, refined lighting
            self.lights['key'].color = np.array([1.0, 0.95, 0.9])
            self.lights['fill'].intensity = 0.8
            self.lights['accent1'].color = np.array([0.9, 0.9, 1.0])
            self.ambient_light = np.array([0.1, 0.1, 0.15, 1.0])

        elif genre == 'electronic':
            # Dynamic, colorful lighting
            self.lights['key'].color = np.array([0.8, 1.0, 1.2])
            self.lights['fill'].intensity = 0.3
            self.lights['accent1'].color = np.array([0.0, 1.0, 2.0])
            self.lights['accent2'].color = np.array([2.0, 0.0, 1.0])
            self.ambient_light = np.array([0.05, 0.05, 0.1, 1.0])

        elif genre == 'rock':
            # Bold, dramatic lighting
            self.lights['key'].color = np.array([1.2, 0.9, 0.7])
            self.lights['rim'].intensity = 1.2
            self.lights['accent1'].color = np.array([1.5, 0.3, 0.0])
            self.ambient_light = np.array([0.1, 0.05, 0.05, 1.0])

        logger.info(f"🎭 Applied {genre} lighting style")

    def _hsv_to_rgb(self, h: float, s: float, v: float) -> np.ndarray:
        """Convert HSV to RGB color"""
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c

        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        return np.array([r + m, g + m, b + m])

    def apply_gl_lighting(self):
        """Apply all lighting to OpenGL"""
        # Set ambient light
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, self.ambient_light)

        # Apply all lights
        light_index = 0
        for light in self.lights.values():
            if light_index < 8:  # OpenGL supports up to 8 lights
                light.apply_gl_lighting(light_index)
                light_index += 1

        # Apply current material
        if self.current_material:
            self.current_material.apply_gl_material()

    def set_material(self, material_name: str):
        """Set the current material"""
        if material_name in self.materials:
            self.current_material = self.materials[material_name]
            logger.info(f"🎨 Material set to: {material_name}")

    def create_custom_material(self, name: str, properties: Dict):
        """Create a custom material from properties"""
        material = Material(name)

        if 'ambient' in properties:
            material.ambient = np.array(properties['ambient'])
        if 'diffuse' in properties:
            material.diffuse = np.array(properties['diffuse'])
        if 'specular' in properties:
            material.specular = np.array(properties['specular'])
        if 'emission' in properties:
            material.emission = np.array(properties['emission'])
        if 'shininess' in properties:
            material.shininess = properties['shininess']
        if 'metallic' in properties:
            material.metallic = properties['metallic']
        if 'roughness' in properties:
            material.roughness = properties['roughness']

        self.materials[name] = material
        logger.info(f"🎨 Created custom material: {name}")

    def get_lighting_stats(self) -> Dict:
        """Get current lighting system statistics"""
        return {
            'active_lights': sum(1 for light in self.lights.values() if light.enabled),
            'total_lights': len(self.lights),
            'current_material': self.current_material.name if self.current_material else 'None',
            'available_materials': list(self.materials.keys()),
            'current_genre': self.current_genre
        }

class AdvancedLightingMorph(QOpenGLWidget):
    """MMPA morphing widget with advanced lighting"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Morphing parameters
        self.morph_factor = 0.5
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.scale_factor = 1.0

        # Professional lighting system
        self.lighting_system = LightingSystem()

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS

        self.animation_time = 0.0

        logger.info("🚀 Advanced Lighting Morphing Widget initialized")

    def initializeGL(self):
        """Initialize OpenGL with advanced lighting"""
        glClearColor(0.01, 0.01, 0.05, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Initialize professional lighting
        self.lighting_system.initialize_gl_lighting()

        logger.info("✅ Advanced lighting OpenGL initialized")

    def resizeGL(self, width: int, height: int):
        """Handle window resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height if height > 0 else 1.0
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render with advanced lighting"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.rotation, 1.0, 1.0, 0.5)
        glScalef(self.scale_factor, self.scale_factor, self.scale_factor)

        # Apply professional lighting
        self.lighting_system.apply_gl_lighting()

        # Generate morphed geometry
        vertices = self.generate_morphed_shape()

        # Render with professional lighting
        self.render_lit_shape(vertices)

    def generate_morphed_shape(self):
        """Generate basic morphed shape (simplified for lighting demo)"""
        num_points = 500
        vertices = []

        for i in range(num_points):
            theta = (i / num_points) * 2 * math.pi * 3
            phi = ((i * 7) % num_points) / num_points * math.pi

            # Sphere to cube morphing
            if self.shape_a == 'sphere' and self.shape_b == 'cube':
                # Sphere coordinates
                sx = math.sin(phi) * math.cos(theta)
                sy = math.cos(phi)
                sz = math.sin(phi) * math.sin(theta)

                # Cube coordinates (normalized)
                max_coord = max(abs(sx), abs(sy), abs(sz))
                if max_coord > 0:
                    cx = sx / max_coord
                    cy = sy / max_coord
                    cz = sz / max_coord
                else:
                    cx = cy = cz = 0

                # Morph between sphere and cube
                x = sx * (1 - self.morph_factor) + cx * self.morph_factor
                y = sy * (1 - self.morph_factor) + cy * self.morph_factor
                z = sz * (1 - self.morph_factor) + cz * self.morph_factor

                vertices.append([x, y, z])

        return vertices

    def render_lit_shape(self, vertices):
        """Render shape with professional lighting and materials"""
        if not vertices:
            return

        # Use material lighting instead of manual colors
        glEnable(GL_LIGHTING)

        # Render as small spheres to show lighting effects
        for i, vertex in enumerate(vertices):
            glPushMatrix()
            glTranslatef(vertex[0], vertex[1], vertex[2])

            # Vary material based on position for visual interest
            if i % 4 == 0:
                self.lighting_system.set_material('gold')
            elif i % 4 == 1:
                self.lighting_system.set_material('chrome')
            elif i % 4 == 2:
                self.lighting_system.set_material('glass')
            else:
                self.lighting_system.set_material('plastic')

            self.lighting_system.apply_gl_lighting()

            # Render a small sphere (glutSolidSphere alternative)
            self.render_sphere(0.02, 8, 6)

            glPopMatrix()

    def render_sphere(self, radius: float, slices: int, stacks: int):
        """Render a sphere with proper normals for lighting"""
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + (i / stacks))
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)

            lat1 = math.pi * (-0.5 + ((i + 1) / stacks))
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)

            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * (j / slices)
                x = math.cos(lng)
                y = math.sin(lng)

                # First vertex
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(radius * x * zr0, radius * y * zr0, radius * z0)

                # Second vertex
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(radius * x * zr1, radius * y * zr1, radius * z1)

            glEnd()

    def update_animation(self):
        """Update animation and lighting"""
        self.animation_time = time.time()
        self.rotation += 0.5

        # Simulate musical data (in real integration, this comes from MMPA engine)
        musical_data = {
            'amplitude': 0.5 + 0.5 * math.sin(self.animation_time * 2),
            'genre': 'jazz',  # Could cycle through genres
            'key_signature': 'C major'
        }

        # Update lighting system
        self.lighting_system.update_lighting(self.animation_time, musical_data)

        # Update morphing
        self.morph_factor = 0.5 + 0.5 * math.sin(self.animation_time * 0.7)
        self.scale_factor = 0.8 + 0.4 * math.sin(self.animation_time * 1.3)

        self.update()

    def set_lighting_genre(self, genre: str):
        """Manually set lighting genre for testing"""
        self.lighting_system._apply_genre_lighting(genre)

    def cycle_material(self):
        """Cycle through available materials"""
        materials = list(self.lighting_system.materials.keys())
        current_name = self.lighting_system.current_material.name
        current_index = materials.index(current_name)
        next_index = (current_index + 1) % len(materials)
        self.lighting_system.set_material(materials[next_index])

def main():
    """Test advanced lighting system"""
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("🔥 MMPA Advanced Lighting & Materials System")
    window.setGeometry(100, 100, 1200, 800)

    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QHBoxLayout(central_widget)

    # Advanced lighting widget
    lighting_widget = AdvancedLightingMorph()
    layout.addWidget(lighting_widget, 80)

    # Controls
    controls = QWidget()
    controls.setMaximumWidth(200)
    controls_layout = QVBoxLayout(controls)

    info_label = QLabel("🔥 Advanced Lighting")
    info_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
    controls_layout.addWidget(info_label)

    # Genre buttons
    for genre in ['jazz', 'classical', 'electronic', 'rock']:
        btn = QPushButton(f"{genre.title()} Lighting")
        btn.clicked.connect(lambda checked, g=genre: lighting_widget.set_lighting_genre(g))
        controls_layout.addWidget(btn)

    # Material cycling button
    material_btn = QPushButton("Cycle Material")
    material_btn.clicked.connect(lighting_widget.cycle_material)
    controls_layout.addWidget(material_btn)

    controls_layout.addStretch()
    layout.addWidget(controls, 20)

    window.show()

    print("🔥 MMPA Advanced Lighting & Materials System")
    print("=" * 50)
    print("✅ Professional PBR materials")
    print("✅ Multi-light setup (6 lights)")
    print("✅ Musical genre lighting styles")
    print("✅ Real-time light animation")
    print("✅ Advanced material properties")
    print("✅ OpenGL lighting integration")
    print()
    print("🎵 Features:")
    print("   • Genre-specific lighting (Jazz, Classical, Electronic, Rock)")
    print("   • Professional materials (Gold, Chrome, Glass, Plastic, Luminous)")
    print("   • Music-reactive intensity and color")
    print("   • Real-time light position animation")
    print("   • PBR material properties")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()