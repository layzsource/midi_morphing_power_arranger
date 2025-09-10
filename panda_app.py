import sys
import os
import queue
import numpy as np

# Panda3D imports
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight, DirectionalLight, PointLight, Vec4, Vec3, WindowProperties,
    NodePath, Shader, ShaderAttrib, Texture, TextureStage, Point3,
    TransparencyAttrib, Loader
)
from direct.filter.CommonFilters import CommonFilters
from direct.particles.ParticleEffect import ParticleEffect
from direct.task import Task

class PandaApp(ShowBase):
    def __init__(self, data_queue):
        ShowBase.__init__(self)
        self.data_queue = data_queue
        
        # --- Window and Basic Setup ---
        props = WindowProperties()
        props.set_size(1280, 720)
        self.win.request_properties(props)
        self.setBackgroundColor(0, 0, 0, 1) # Black background

        # Disable the default camera control
        self.disable_mouse()
        self.camera.set_pos(0, -30, 10)
        self.camera.look_at(0, 0, 0)

        # --- Scene Lighting ---
        # Overall ambient light
        ambient_light = AmbientLight("ambient")
        ambient_light.setColor(Vec4(0.2, 0.2, 0.2, 1))
        self.render.setLight(self.render.attachNewNode(ambient_light))

        # A directional light to give some definition
        directional_light = DirectionalLight("directional")
        directional_light.setDirection(Vec3(1, 1, -1))
        directional_light.setColor(Vec4(0.5, 0.5, 0.5, 1))
        directional_light_np = self.render.attachNewNode(directional_light)
        self.render.setLight(directional_light_np)

        # --- Water Environment (Shader-based) ---
        self.water_node = self.loader.loadModel("models/plane")
        self.water_node.reparentTo(self.render)
        self.water_node.setPos(0, 0, -2)
        self.water_node.setScale(50)
        self.water_shader = Shader.load(
            Shader.SL_GLSL,
            vertex="shaders/water_shader.vert",
            fragment="shaders/water_shader.frag"
        )
        self.water_node.setShader(self.water_shader)
        self.water_node.setShaderInput("time", 0.0)
        
        # Dynamic texture for reflection (render-to-texture)
        self.water_reflection_cam = self.make_camera(self.win, stereo=None, scene=self.render)
        self.water_reflection_cam.reparentTo(self.render)
        self.water_reflection_cam.setPos(0, 0, -2) # Position it at the same location as the water
        self.water_reflection_texture = Texture()
        self.water_reflection_buffer = self.win.make_texture_buffer(
            "water_reflection_buffer", 512, 512, self.water_reflection_texture
        )
        self.water_reflection_cam.set_display_region_clear_color(Vec4(0, 0, 0, 1))
        self.water_reflection_cam.get_display_region(0).set_clear_color(True)
        self.water_node.setShaderInput("reflection_map", self.water_reflection_texture)

        # --- Sonoluminescence Bubble ---
        self.bubble = self.loader.loadModel("models/sphere")
        self.bubble.reparentTo(self.render)
        self.bubble.setPos(0, 0, -1)
        self.bubble_shader = Shader.load(
            Shader.SL_GLSL,
            vertex="shaders/bubble_shader.vert",
            fragment="shaders/bubble_shader.frag"
        )
        self.bubble.setShader(self.bubble_shader)
        self.bubble.setTransparency(TransparencyAttrib.M_alpha)
        self.bubble.setShaderInput("peak_temp", 0.0)

        # --- Light Flash Effect ---
        self.flash_light = PointLight('flash_light')
        self.flash_light_np = self.render.attachNewNode(self.flash_light)
        self.flash_light_np.setPos(0, 0, -1)
        self.flash_light.setAttenuation(Point3(0, 0, 0.001)) # Inverse square falloff
        self.flash_light.setColor(Vec4(0, 0, 0, 1)) # Starts off
        self.render.setLight(self.flash_light_np)

        # --- Shockwave Particle System ---
        self.shockwave_effect = ParticleEffect()
        self.shockwave_effect.loadConfig("shockwave.ptf") # Load from a particle config file
        self.shockwave_effect.setPos(0, 0, -1)
        self.shockwave_effect.start(self.render)
        self.shockwave_effect.disable()

        # --- Post-processing: Bloom Filter ---
        self.filters = CommonFilters(self.win, self.cam)
        if self.filters.support_bloom:
            self.filters.setBloom(
                blend=(0, 0, 0, 1),
                desat=-0.5,
                intensity=3.0,
                size="large"
            )
            print("✓ Bloom filter enabled.")
        else:
            print("⚠ Bloom filter not supported.")

        # --- Task for updating visualization ---
        self.taskMgr.add(self.update_visualization, "update_visualization")

    def update_visualization(self, task):
        # Update water shader time uniform
        self.water_node.setShaderInput("time", task.time)
        
        # Check for new data from the C++ physics engine
        try:
            state_data = self.data_queue.get_nowait()
            self.update_state(state_data)
        except queue.Empty:
            pass
        
        return Task.cont

    def update_state(self, state_data):
        # Update bubble size
        self.bubble.setScale(state_data['bubble_radius'] * 1000)
        
        # Update bubble shader uniforms for emission
        self.bubble.setShaderInput("peak_temp", state_data['peak_temperature'])
        
        # Update light flash based on intensity
        flash_intensity = state_data['light_intensity']
        self.flash_light.setColor(Vec4(flash_intensity, flash_intensity, flash_intensity, 1))
        
        # Trigger shockwave effect based on threshold
        if state_data['peak_temperature'] > 50000 and not self.shockwave_effect.is_enabled():
            self.shockwave_effect.start()
        elif state_data['peak_temperature'] <= 50000 and self.shockwave_effect.is_enabled():
            self.shockwave_effect.disable()

### `shaders/water_shader.vert`
```glsl
#version 130

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform vec4 p3d_Color;
uniform float time;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec4 vtx_color;
out vec2 vtx_texcoord;
out vec3 vtx_normal;
out vec3 vtx_position;
out vec3 vtx_eyevec;

void main() {
    vtx_color = p3d_Color;
    vtx_texcoord = p3d_MultiTexCoord0;
    vtx_normal = normalize(p3d_NormalMatrix * p3d_Normal);
    vec4 position = p3d_ModelViewMatrix * p3d_Vertex;
    vtx_position = position.xyz;
    vtx_eyevec = normalize(-vtx_position);

    // Dynamic wave effect
    float waves = sin(p3d_Vertex.x * 0.5 + time * 2.0) * 0.1 + cos(p3d_Vertex.y * 0.5 + time * 2.0) * 0.1;
    gl_Position = p3d_ModelViewProjectionMatrix * (p3d_Vertex + vec4(0, 0, waves, 0));
}
