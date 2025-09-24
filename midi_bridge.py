#!/usr/bin/env python3
"""
MIDI Bridge for Universal Signal Engine
Connects Python MIDI processing to web interface via WebSocket
Integrates with existing working_full_app_backup.py functionality
"""

import asyncio
import websockets
import json
import pygame
import pygame.midi
import threading
import time
from typing import Dict, Any, Optional

class MIDIBridge:
    def __init__(self, websocket_port: int = 8765):
        self.websocket_port = websocket_port
        self.clients = set()
        self.midi_input = None
        self.running = False

        # MIDI state tracking
        self.cc_values = {}  # Store current CC values
        self.note_states = {}  # Store note on/off states

        # Initialize MIDI
        pygame.init()
        pygame.midi.init()

    async def register_client(self, websocket, path):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")

        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            print(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_midi_data(self, data: Dict[str, Any]):
        """Send MIDI data to all connected web clients"""
        if self.clients:
            message = json.dumps(data)
            # Send to all clients, remove any that are disconnected
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)

            # Clean up disconnected clients
            for client in disconnected:
                self.clients.discard(client)

    def setup_midi_input(self):
        """Setup MIDI input device (matches working_full_app_backup.py logic)"""
        device_count = pygame.midi.get_count()
        print(f"Found {device_count} MIDI devices")

        for device_id in range(device_count):
            info = pygame.midi.get_device_info(device_id)
            name = info[1].decode()
            is_input = info[2]

            print(f"Device {device_id}: {name} ({'input' if is_input else 'output'})")

            # Connect to IAC Driver Bus 1 or first available input
            if is_input and ('IAC Driver' in name or self.midi_input is None):
                try:
                    self.midi_input = pygame.midi.Input(device_id)
                    print(f"✓ Connected to MIDI device: {name}")
                    return True
                except Exception as e:
                    print(f"✗ Failed to connect to {name}: {e}")

        print("✗ No MIDI input device found")
        return False

    def process_midi_messages(self):
        """Process MIDI messages in separate thread"""
        while self.running and self.midi_input:
            if self.midi_input.poll():
                midi_events = self.midi_input.read(10)

                for event in midi_events:
                    status, data1, data2, data3 = event[0]
                    timestamp = event[1]

                    # Process CC messages
                    if 176 <= status <= 191:  # Control Change
                        channel = status - 176
                        cc_number = data1
                        cc_value = data2

                        self.cc_values[cc_number] = cc_value

                        # Send to web clients
                        asyncio.create_task(self.broadcast_midi_data({
                            'type': 'cc',
                            'channel': channel,
                            'cc': cc_number,
                            'value': cc_value,
                            'normalized': cc_value / 127.0,
                            'timestamp': timestamp
                        }))

                        print(f"CC{cc_number}: {cc_value} (normalized: {cc_value/127.0:.3f})")

                    # Process Note On/Off messages
                    elif 144 <= status <= 159:  # Note On
                        channel = status - 144
                        note = data1
                        velocity = data2

                        if velocity > 0:
                            self.note_states[note] = velocity
                            asyncio.create_task(self.broadcast_midi_data({
                                'type': 'note_on',
                                'channel': channel,
                                'note': note,
                                'velocity': velocity,
                                'normalized_velocity': velocity / 127.0,
                                'timestamp': timestamp
                            }))
                        else:
                            # Velocity 0 = note off
                            if note in self.note_states:
                                del self.note_states[note]
                            asyncio.create_task(self.broadcast_midi_data({
                                'type': 'note_off',
                                'channel': channel,
                                'note': note,
                                'timestamp': timestamp
                            }))

                    elif 128 <= status <= 143:  # Note Off
                        channel = status - 128
                        note = data1

                        if note in self.note_states:
                            del self.note_states[note]

                        asyncio.create_task(self.broadcast_midi_data({
                            'type': 'note_off',
                            'channel': channel,
                            'note': note,
                            'timestamp': timestamp
                        }))

            time.sleep(0.001)  # Small delay to prevent CPU overload

    async def start_server(self):
        """Start WebSocket server"""
        print(f"Starting MIDI Bridge WebSocket server on port {self.websocket_port}")

        if not self.setup_midi_input():
            print("Failed to setup MIDI input")
            return

        self.running = True

        # Start MIDI processing thread
        midi_thread = threading.Thread(target=self.process_midi_messages)
        midi_thread.daemon = True
        midi_thread.start()

        # Start WebSocket server
        async with websockets.serve(self.register_client, "localhost", self.websocket_port):
            print(f"🎵 MIDI Bridge running on ws://localhost:{self.websocket_port}")
            print("Ready to bridge MIDI data to web interface!")

            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                print("Shutting down MIDI Bridge...")
                self.running = False
                if self.midi_input:
                    self.midi_input.close()
                pygame.midi.quit()
                pygame.quit()

if __name__ == "__main__":
    bridge = MIDIBridge()
    asyncio.run(bridge.start_server())