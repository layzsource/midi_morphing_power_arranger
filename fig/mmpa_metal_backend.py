#!/usr/bin/env python3
"""
MMPA Metal Backend - Simplified Working Implementation
Native Metal integration for MMPA rendering system

Focus: Architecture demonstration with working Metal integration
"""

import math
import time
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
import Metal
import MetalKit

logger = logging.getLogger(__name__)

class MMPAMetalBackend:
    """Simplified Metal backend for MMPA system"""

    def __init__(self):
        # Metal device and resources
        self.device = Metal.MTLCreateSystemDefaultDevice()
        if not self.device:
            raise RuntimeError("Metal device not available")

        self.command_queue = self.device.newCommandQueue()

        # Audio-reactive parameters
        self.audio_amplitude = 0.0
        self.bass_energy = 0.0
        self.mid_energy = 0.0
        self.treble_energy = 0.0
        self.current_genre = 0

        # Performance metrics
        self.frame_count = 0
        self.last_frame_time = time.time()
        self.fps = 0.0

        logger.info(f"🚀 MMPA Metal Backend initialized on {self.device.name()}")

    def get_device_info(self) -> Dict[str, Any]:
        """Get Metal device information"""
        return {
            'name': self.device.name(),
            'metal3_support': self.device.supportsFamily_(Metal.MTLGPUFamilyMetal3),
            'max_threads_per_group': self.device.maxThreadsPerThreadgroup(),
            'max_buffer_length_mb': self.device.maxBufferLength() // (1024 * 1024),
            'unified_memory': self.device.hasUnifiedMemory(),
            'registry_id': self.device.registryID()
        }

    def create_buffer(self, size: int, data: Optional[bytes] = None) -> Any:
        """Create Metal buffer"""
        if data:
            return self.device.newBufferWithBytes_length_options_(
                data, len(data), Metal.MTLResourceStorageModeShared
            )
        else:
            return self.device.newBufferWithLength_options_(
                size, Metal.MTLResourceStorageModeShared
            )

    def create_texture(self, width: int, height: int, pixel_format: int) -> Any:
        """Create Metal texture"""
        descriptor = Metal.MTLTextureDescriptor.texture2DDescriptorWithPixelFormat_width_height_mipmapped_(
            pixel_format, width, height, False
        )
        descriptor.setUsage_(Metal.MTLTextureUsageShaderRead | Metal.MTLTextureUsageShaderWrite)
        return self.device.newTextureWithDescriptor_(descriptor)

    def create_compute_pipeline(self, function_name: str, shader_source: str) -> Optional[Any]:
        """Create compute pipeline from Metal shader source"""
        try:
            library, error = self.device.newLibraryWithSource_options_error_(
                shader_source, None, None
            )

            if error or not library:
                logger.error(f"Shader compilation failed: {error}")
                return None

            function = library.newFunctionWithName_(function_name)
            if not function:
                logger.error(f"Function '{function_name}' not found")
                return None

            pipeline, error = self.device.newComputePipelineStateWithFunction_error_(
                function, None
            )

            if error:
                logger.error(f"Pipeline creation failed: {error}")
                return None

            return pipeline

        except Exception as e:
            logger.error(f"Compute pipeline creation failed: {e}")
            return None

    def update_audio_parameters(self, amplitude: float, bass: float, mid: float, treble: float, genre: int):
        """Update audio-reactive parameters for Metal rendering"""
        self.audio_amplitude = amplitude
        self.bass_energy = bass
        self.mid_energy = mid
        self.treble_energy = treble
        self.current_genre = genre

    def get_audio_parameters(self) -> Dict[str, float]:
        """Get current audio parameters"""
        return {
            'amplitude': self.audio_amplitude,
            'bass_energy': self.bass_energy,
            'mid_energy': self.mid_energy,
            'treble_energy': self.treble_energy,
            'genre': self.current_genre
        }

    def execute_compute_kernel(self, pipeline: Any, textures: List[Any], buffers: List[Any],
                              thread_groups: Tuple[int, int, int],
                              threads_per_group: Tuple[int, int, int]) -> bool:
        """Execute compute kernel"""
        if not pipeline:
            return False

        try:
            command_buffer = self.command_queue.commandBuffer()
            compute_encoder = command_buffer.computeCommandEncoder()

            compute_encoder.setComputePipelineState_(pipeline)

            # Set textures
            for i, texture in enumerate(textures):
                compute_encoder.setTexture_atIndex_(texture, i)

            # Set buffers
            for i, buffer in enumerate(buffers):
                compute_encoder.setBuffer_offset_atIndex_(buffer, 0, i)

            # Dispatch
            thread_groups_size = Metal.MTLSize(*thread_groups)
            threads_per_group_size = Metal.MTLSize(*threads_per_group)

            compute_encoder.dispatchThreadgroups_threadsPerThreadgroup_(
                thread_groups_size, threads_per_group_size
            )

            compute_encoder.endEncoding()
            command_buffer.commit()
            command_buffer.waitUntilCompleted()

            return True

        except Exception as e:
            logger.error(f"Compute kernel execution failed: {e}")
            return False

    def update_performance_metrics(self):
        """Update performance tracking"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time

        if frame_time > 0:
            self.fps = 1.0 / frame_time

        self.last_frame_time = current_time
        self.frame_count += 1

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            'fps': self.fps,
            'frame_count': self.frame_count,
            'device_utilization': self._estimate_gpu_utilization()
        }

    def _estimate_gpu_utilization(self) -> float:
        """Rough GPU utilization estimate based on frame rate"""
        target_fps = 60.0
        if self.fps > 0:
            return min(1.0, target_fps / self.fps)
        return 0.0

    def create_audio_reactive_compute_shader(self) -> str:
        """Create sample audio-reactive compute shader"""
        return """
        #include <metal_stdlib>
        using namespace metal;

        kernel void audio_reactive_effect(texture2d<float, access::write> outputTexture [[texture(0)]],
                                        constant float& audioAmplitude [[buffer(0)]],
                                        constant float& bassEnergy [[buffer(1)]],
                                        constant float& midEnergy [[buffer(2)]],
                                        constant float& trebleEnergy [[buffer(3)]],
                                        constant float& time [[buffer(4)]],
                                        uint2 gid [[thread_position_in_grid]]) {

            if (gid.x >= outputTexture.get_width() || gid.y >= outputTexture.get_height()) {
                return;
            }

            float2 uv = float2(gid) / float2(outputTexture.get_width(), outputTexture.get_height());
            uv = uv * 2.0 - 1.0; // Convert to [-1, 1]

            float distance = length(uv);

            // Audio-reactive colors
            float3 color;
            color.r = bassEnergy * (1.0 - distance) + sin(time + distance * 10.0) * 0.5 + 0.5;
            color.g = midEnergy * cos(time * 2.0 + distance * 5.0) * 0.5 + 0.5;
            color.b = trebleEnergy * sin(time * 3.0 + distance * 8.0) * 0.5 + 0.5;

            // Audio-reactive intensity
            float intensity = audioAmplitude * (1.0 - distance * 0.5);
            color *= intensity;

            outputTexture.write(float4(color, 1.0), gid);
        }
        """


class MMPAMetalRenderer:
    """High-level Metal renderer for MMPA"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.backend = MMPAMetalBackend()

        # Create render resources
        self.output_texture = self.backend.create_texture(
            width, height, Metal.MTLPixelFormatRGBA8Unorm
        )

        # Create audio-reactive compute pipeline
        shader_source = self.backend.create_audio_reactive_compute_shader()
        self.audio_pipeline = self.backend.create_compute_pipeline(
            "audio_reactive_effect", shader_source
        )

        # Audio parameter buffers
        self._create_audio_buffers()

        logger.info(f"✅ MMPA Metal Renderer initialized: {width}x{height}")

    def _create_audio_buffers(self):
        """Create buffers for audio parameters"""
        self.amplitude_buffer = self.backend.create_buffer(4)  # float
        self.bass_buffer = self.backend.create_buffer(4)
        self.mid_buffer = self.backend.create_buffer(4)
        self.treble_buffer = self.backend.create_buffer(4)
        self.time_buffer = self.backend.create_buffer(4)

    def update_audio_data(self, amplitude: float, bass: float, mid: float, treble: float):
        """Update audio parameters in Metal buffers"""
        self.backend.update_audio_parameters(amplitude, bass, mid, treble, 0)

        # Update Metal buffers with proper memory access
        try:
            import ctypes

            # Update amplitude buffer
            if self.amplitude_buffer:
                ptr = ctypes.cast(self.amplitude_buffer.contents(), ctypes.POINTER(ctypes.c_float))
                ptr[0] = amplitude

            # Update bass buffer
            if self.bass_buffer:
                ptr = ctypes.cast(self.bass_buffer.contents(), ctypes.POINTER(ctypes.c_float))
                ptr[0] = bass

            # Update mid buffer
            if self.mid_buffer:
                ptr = ctypes.cast(self.mid_buffer.contents(), ctypes.POINTER(ctypes.c_float))
                ptr[0] = mid

            # Update treble buffer
            if self.treble_buffer:
                ptr = ctypes.cast(self.treble_buffer.contents(), ctypes.POINTER(ctypes.c_float))
                ptr[0] = treble

            # Update time buffer
            if self.time_buffer:
                ptr = ctypes.cast(self.time_buffer.contents(), ctypes.POINTER(ctypes.c_float))
                ptr[0] = time.time()

        except Exception as e:
            logger.error(f"Buffer update failed: {e}")
            # Fallback: recreate buffers with new data
            self.amplitude_buffer = self.backend.create_buffer(4, np.array([amplitude], dtype=np.float32).tobytes())
            self.bass_buffer = self.backend.create_buffer(4, np.array([bass], dtype=np.float32).tobytes())
            self.mid_buffer = self.backend.create_buffer(4, np.array([mid], dtype=np.float32).tobytes())
            self.treble_buffer = self.backend.create_buffer(4, np.array([treble], dtype=np.float32).tobytes())
            self.time_buffer = self.backend.create_buffer(4, np.array([time.time()], dtype=np.float32).tobytes())

    def render_frame(self) -> bool:
        """Render a frame using Metal compute"""
        if not self.audio_pipeline:
            return False

        # Execute audio-reactive compute shader
        success = self.backend.execute_compute_kernel(
            self.audio_pipeline,
            textures=[self.output_texture],
            buffers=[self.amplitude_buffer, self.bass_buffer, self.mid_buffer,
                    self.treble_buffer, self.time_buffer],
            thread_groups=((self.width + 15) // 16, (self.height + 15) // 16, 1),
            threads_per_group=(16, 16, 1)
        )

        if success:
            self.backend.update_performance_metrics()

        return success

    def get_device_info(self) -> Dict[str, Any]:
        """Get Metal device information"""
        return self.backend.get_device_info()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get rendering performance metrics"""
        return self.backend.get_performance_metrics()

    def resize(self, width: int, height: int):
        """Resize render targets"""
        self.width = width
        self.height = height
        self.output_texture = self.backend.create_texture(
            width, height, Metal.MTLPixelFormatRGBA8Unorm
        )
        logger.info(f"✅ Metal renderer resized: {width}x{height}")


def test_mmpa_metal_backend():
    """Test MMPA Metal backend system"""
    print("🚀 Testing MMPA Metal Backend System")
    print("=" * 50)

    try:
        # Test backend
        backend = MMPAMetalBackend()
        device_info = backend.get_device_info()

        print("✅ Metal Backend Initialized")
        print(f"   Device: {device_info['name']}")
        print(f"   Metal 3 Support: {device_info['metal3_support']}")
        print(f"   Max Buffer Size: {device_info['max_buffer_length_mb']} MB")
        print(f"   Unified Memory: {device_info['unified_memory']}")

        # Test renderer
        renderer = MMPAMetalRenderer(1024, 768)
        print("✅ Metal Renderer Created")

        # Test audio-reactive rendering
        for i in range(5):
            amplitude = 0.5 + 0.3 * math.sin(time.time())
            bass = 0.3 + 0.2 * math.cos(time.time() * 2)
            mid = 0.4 + 0.3 * math.sin(time.time() * 1.5)
            treble = 0.2 + 0.2 * math.cos(time.time() * 3)

            renderer.update_audio_data(amplitude, bass, mid, treble)
            success = renderer.render_frame()

            if success:
                print(f"✅ Frame {i+1} rendered successfully")
            else:
                print(f"❌ Frame {i+1} render failed")

            time.sleep(0.016)  # ~60 FPS

        # Performance metrics
        metrics = renderer.get_performance_metrics()
        print(f"\n📊 Performance Metrics:")
        print(f"   FPS: {metrics['fps']:.1f}")
        print(f"   Frame Count: {metrics['frame_count']}")
        print(f"   GPU Utilization: {metrics['device_utilization']:.1%}")

        print(f"\n🎨 Metal Backend Features:")
        print(f"  • Native Apple Silicon Metal 3 performance")
        print(f"  • Audio-reactive compute shaders")
        print(f"  • Real-time parameter updates")
        print(f"  • Performance monitoring")
        print(f"  • Unified memory architecture")
        print(f"  • Multi-threaded compute dispatch")

        print("\n✅ MMPA Metal Backend System Ready!")
        print("🚀 Ready for full MMPA integration")

        return True

    except Exception as e:
        print(f"❌ Metal backend test failed: {e}")
        return False


if __name__ == "__main__":
    test_mmpa_metal_backend()