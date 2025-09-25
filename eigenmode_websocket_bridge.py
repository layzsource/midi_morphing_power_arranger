#!/usr/bin/env python3
"""
🌊 Eigenmode WebSocket Bridge
Streams real-time spectral coefficients from Signal→Form Engine to eigenmode_cube.html
"""

import asyncio
import websockets
import json
import time
import math
import random
from typing import Dict, List, Any

class EigenmodeStreamServer:
    def __init__(self, port: int = 7070):
        self.port = port
        self.clients = set()
        self.running = True

        # Synthetic data for testing (replace with real SpectralGraphEngine output)
        self.coeffs = [0.2, 0.4, 0.3, 0.2]  # c[0..3] for φ₀..φ₃
        self.pmw = 0.5  # Pineal mod wheel

        print(f"🌊 Eigenmode bridge starting on ws://localhost:{port}")

    async def register_client(self, websocket, path):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        print(f"📡 Client connected: {len(self.clients)} total")

        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"📡 Client disconnected: {len(self.clients)} total")

    async def broadcast_frame(self, frame_data: Dict[str, Any]):
        """Send frame to all connected clients"""
        if not self.clients:
            return

        message = json.dumps(frame_data)
        dead_clients = []

        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                dead_clients.append(client)
            except Exception as e:
                print(f"❌ Broadcast error: {e}")
                dead_clients.append(client)

        # Clean up dead connections
        for client in dead_clients:
            self.clients.discard(client)

    def generate_synthetic_data(self, t: float) -> Dict[str, Any]:
        """Generate synthetic eigenmode data for testing"""

        # Simulate musical input driving eigenmodes
        # φ₀ (breathing): Low frequency base
        c0 = 0.3 + 0.2 * math.sin(t * 0.5)

        # φ₁ (twisting): Mid frequency modulation
        c1 = 0.4 + 0.3 * math.sin(t * 1.2 + math.pi/3)

        # φ₂ (bending): High frequency accent
        c2 = 0.2 + 0.3 * math.sin(t * 2.1 + math.pi/2)

        # φ₃ (rippling): Chaotic detail
        c3 = 0.1 + 0.2 * (math.sin(t * 3.7) * math.cos(t * 1.9))

        # PMW follows unity/consciousness depth
        pmw_base = 0.5 + 0.3 * math.sin(t * 0.3)
        pmw = max(0, min(1, pmw_base))

        return {
            "c": [c0, c1, c2, c3],
            "pmw": pmw,
            "timestamp": time.time(),
            "frame": int(t * 60)  # Assume 60 FPS
        }

    def simulate_midi_input(self, cc_values: Dict[int, int]) -> Dict[str, Any]:
        """Convert MIDI CC values to eigenmode coefficients"""

        # Map MIDI CCs to eigenmode weights
        cc1 = cc_values.get(1, 64) / 127.0  # Mod wheel → φ₀ (breathing)
        cc2 = cc_values.get(2, 64) / 127.0  # Pitch wheel → φ₁ (twisting)
        cc4 = cc_values.get(4, 64) / 127.0  # CC4 → φ₂ (bending)
        cc7 = cc_values.get(7, 100) / 127.0 # Volume → φ₃ (rippling)

        # PMW from expression pedal or computed unity
        pmw = cc_values.get(11, 64) / 127.0  # Expression

        return {
            "c": [cc1, cc2, cc4, cc7],
            "pmw": pmw,
            "timestamp": time.time(),
            "source": "midi"
        }

    async def data_generator(self):
        """Main data generation loop"""
        start_time = time.time()
        frame_count = 0

        while self.running:
            current_time = time.time()
            elapsed = current_time - start_time

            # Generate frame data
            frame_data = self.generate_synthetic_data(elapsed)

            # Broadcast to all clients
            await self.broadcast_frame(frame_data)

            frame_count += 1
            if frame_count % 300 == 0:  # Log every 5 seconds at 60fps
                print(f"🌊 Streamed {frame_count} frames, {len(self.clients)} clients")

            # Maintain ~60 FPS
            await asyncio.sleep(1/60.0)

    async def start_server(self):
        """Start WebSocket server and data generator"""

        # Start WebSocket server
        server = await websockets.serve(
            self.register_client,
            "localhost",
            self.port,
            ping_interval=None,  # Disable ping/pong for performance
            ping_timeout=None
        )

        print(f"🚀 Server running on ws://localhost:{self.port}")
        print("📖 Open eigenmode_cube.html in browser to see live visualization")

        # Start data generator
        data_task = asyncio.create_task(self.data_generator())

        try:
            await server.wait_closed()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.running = False
            data_task.cancel()
            server.close()
            await server.wait_closed()

# Integration hook for real SpectralGraphEngine
class SpectralEngineAdapter:
    """Adapter to connect real SpectralGraphEngine output to WebSocket stream"""

    def __init__(self, server: EigenmodeStreamServer):
        self.server = server
        self.last_frame_time = 0

    async def process_spectral_state(self, spectral_state, modal_coefficients):
        """Convert SpectralGraphEngine state to eigenmode frame"""

        current_time = time.time()

        # Throttle to 60 FPS
        if current_time - self.last_frame_time < 1/60.0:
            return

        self.last_frame_time = current_time

        # Extract first 4 modal coefficients for the cube viewer
        c = list(modal_coefficients[:4]) if len(modal_coefficients) >= 4 else [0, 0, 0, 0]

        # Map spectral parameters to PMW
        pmw = spectral_state.get('unity', 0.5)  # Unity parameter → consciousness depth

        frame_data = {
            "c": c,
            "pmw": pmw,
            "timestamp": current_time,
            "source": "spectral_engine",
            "entropy": spectral_state.get('entropy', 0),
            "stokes": spectral_state.get('stokesParameters', {}),
            "temporal_change": spectral_state.get('temporalChange', 0)
        }

        await self.server.broadcast_frame(frame_data)

async def main():
    """Main entry point"""
    server = EigenmodeStreamServer(port=7070)

    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("👋 Goodbye!")

if __name__ == "__main__":
    print("🌊 Signal→Form Eigenmode Bridge")
    print("=" * 40)
    asyncio.run(main())