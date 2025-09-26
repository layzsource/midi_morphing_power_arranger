#!/usr/bin/env python3
"""
MIDI Bridge for Universal Signal Engine
Connects Python MIDI processing to web interface via WebSocket
Integrates with existing working_full_app_backup.py functionality

Enhanced with:
- Thread safety using asyncio.Queue
- Comprehensive error handling
- Proper resource cleanup
- Connection resilience
"""

import asyncio
import websockets
import json
import pygame
import pygame.midi
import threading
import time
import logging
from typing import Dict, Any, Optional, Set

class MIDIBridge:
    def __init__(self, websocket_port: int = 8765):
        self.websocket_port = websocket_port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.midi_input = None
        self.running = False
        self.logger = logging.getLogger(__name__)

        # Thread-safe communication
        self.message_queue: asyncio.Queue = None
        self.loop: asyncio.AbstractEventLoop = None

        # MIDI state tracking with thread safety
        self.cc_values = {}  # Store current CC values
        self.note_states = {}  # Store note on/off states
        self._state_lock = threading.Lock()

        # Device configuration
        self.target_device_names = ['IAC Driver', 'loopMIDI', 'Virtual MIDI']
        self.reconnect_delay = 5.0
        self.max_reconnect_attempts = 10

        # Initialize MIDI with error handling
        try:
            pygame.init()
            pygame.midi.init()
            self.logger.info("MIDI system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MIDI system: {e}")
            raise

    async def register_client(self, websocket, path):
        """Register new WebSocket client with error handling"""
        try:
            self.clients.add(websocket)
            self.logger.info(f"Client connected from {websocket.remote_address}. Total clients: {len(self.clients)}")

            # Send current MIDI state to new client
            with self._state_lock:
                for cc_num, value in self.cc_values.items():
                    await websocket.send(json.dumps({
                        'type': 'cc',
                        'cc': cc_num,
                        'value': value,
                        'normalized': value / 127.0,
                        'timestamp': time.time(),
                        'initial_state': True
                    }))

            await websocket.wait_closed()
        except Exception as e:
            self.logger.warning(f"Client connection error: {e}")
        finally:
            self.clients.discard(websocket)
            self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def broadcast_midi_data(self, data: Dict[str, Any]):
        """Send MIDI data to all connected web clients with resilient error handling"""
        if not self.clients:
            return

        message = json.dumps(data)
        disconnected = set()

        for client in list(self.clients):  # Create copy to avoid modification during iteration
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                self.logger.warning(f"Failed to send to client {client.remote_address}: {e}")
                disconnected.add(client)

        # Clean up disconnected clients
        for client in disconnected:
            self.clients.discard(client)

    def queue_midi_message(self, data: Dict[str, Any]):
        """Thread-safe method to queue MIDI messages from the MIDI thread"""
        if self.loop and self.message_queue:
            try:
                # Schedule the coroutine in the event loop from the MIDI thread
                asyncio.run_coroutine_threadsafe(
                    self.message_queue.put(data),
                    self.loop
                )
            except Exception as e:
                self.logger.error(f"Failed to queue MIDI message: {e}")

    async def process_message_queue(self):
        """Process queued MIDI messages in the event loop"""
        while self.running:
            try:
                # Wait for messages with timeout to allow clean shutdown
                data = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.broadcast_midi_data(data)
            except asyncio.TimeoutError:
                continue  # Normal timeout, keep running
            except Exception as e:
                self.logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(0.1)

    def setup_midi_input(self) -> bool:
        """Setup MIDI input device with comprehensive device detection and error handling"""
        try:
            device_count = pygame.midi.get_count()
            self.logger.info(f"Found {device_count} MIDI devices")

            if device_count == 0:
                self.logger.warning("No MIDI devices found")
                return False

            # First pass: Look for preferred devices
            for device_id in range(device_count):
                try:
                    info = pygame.midi.get_device_info(device_id)
                    if not info:
                        continue

                    name = info[1].decode() if info[1] else f"Unknown Device {device_id}"
                    is_input = bool(info[2])

                    self.logger.debug(f"Device {device_id}: {name} ({'input' if is_input else 'output'})")

                    # Check for preferred device names
                    if is_input and any(target in name for target in self.target_device_names):
                        if self._try_connect_device(device_id, name):
                            return True

                except Exception as e:
                    self.logger.warning(f"Error checking device {device_id}: {e}")
                    continue

            # Second pass: Connect to any available input device
            for device_id in range(device_count):
                try:
                    info = pygame.midi.get_device_info(device_id)
                    if not info:
                        continue

                    name = info[1].decode() if info[1] else f"Unknown Device {device_id}"
                    is_input = bool(info[2])

                    if is_input and self.midi_input is None:
                        if self._try_connect_device(device_id, name):
                            return True

                except Exception as e:
                    self.logger.warning(f"Error in second pass for device {device_id}: {e}")
                    continue

            self.logger.error("No MIDI input device could be connected")
            return False

        except Exception as e:
            self.logger.error(f"Critical error in MIDI setup: {e}")
            return False

    def _try_connect_device(self, device_id: int, name: str) -> bool:
        """Attempt to connect to a specific MIDI device"""
        try:
            self.midi_input = pygame.midi.Input(device_id)
            self.logger.info(f"✓ Connected to MIDI device: {name} (ID: {device_id})")
            return True
        except Exception as e:
            self.logger.warning(f"✗ Failed to connect to {name}: {e}")
            return False

    def process_midi_messages(self):
        """Process MIDI messages in separate thread with comprehensive error handling"""
        self.logger.info("MIDI processing thread started")
        consecutive_errors = 0
        max_consecutive_errors = 10

        while self.running:
            try:
                if not self.midi_input:
                    self.logger.warning("MIDI input lost, attempting to reconnect...")
                    if self.setup_midi_input():
                        consecutive_errors = 0
                        continue
                    else:
                        time.sleep(self.reconnect_delay)
                        continue

                if self.midi_input.poll():
                    try:
                        midi_events = self.midi_input.read(10)
                        consecutive_errors = 0  # Reset error counter on successful read

                        for event in midi_events:
                            try:
                                self._process_single_event(event)
                            except Exception as e:
                                self.logger.warning(f"Error processing MIDI event {event}: {e}")

                    except Exception as e:
                        consecutive_errors += 1
                        self.logger.warning(f"Error reading MIDI events: {e} (consecutive errors: {consecutive_errors})")

                        if consecutive_errors >= max_consecutive_errors:
                            self.logger.error("Too many consecutive MIDI errors, resetting connection")
                            self._reset_midi_connection()
                            consecutive_errors = 0

                time.sleep(0.001)  # Small delay to prevent CPU overload

            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Critical error in MIDI processing: {e}")
                if consecutive_errors >= max_consecutive_errors:
                    self.logger.error("Too many critical errors, stopping MIDI processing")
                    break
                time.sleep(0.1)

        self.logger.info("MIDI processing thread stopped")

    def _process_single_event(self, event):
        """Process a single MIDI event with proper error handling"""
        try:
            status, data1, data2, data3 = event[0]
            timestamp = time.time()  # Use current time for consistency

            # Process CC messages
            if 176 <= status <= 191:  # Control Change
                channel = status - 176
                cc_number = data1
                cc_value = data2

                # Thread-safe state update
                with self._state_lock:
                    self.cc_values[cc_number] = cc_value

                # Queue message for async processing
                self.queue_midi_message({
                    'type': 'cc',
                    'channel': channel,
                    'cc': cc_number,
                    'value': cc_value,
                    'normalized': cc_value / 127.0,
                    'timestamp': timestamp
                })

                self.logger.debug(f"CC{cc_number}: {cc_value} (normalized: {cc_value/127.0:.3f})")

            # Process Note On messages
            elif 144 <= status <= 159:  # Note On
                channel = status - 144
                note = data1
                velocity = data2

                with self._state_lock:
                    if velocity > 0:
                        self.note_states[note] = velocity
                        message_type = 'note_on'
                    else:
                        # Velocity 0 = note off
                        self.note_states.pop(note, None)
                        message_type = 'note_off'

                self.queue_midi_message({
                    'type': message_type,
                    'channel': channel,
                    'note': note,
                    'velocity': velocity,
                    'normalized_velocity': velocity / 127.0,
                    'timestamp': timestamp
                })

            # Process Note Off messages
            elif 128 <= status <= 143:  # Note Off
                channel = status - 128
                note = data1

                with self._state_lock:
                    self.note_states.pop(note, None)

                self.queue_midi_message({
                    'type': 'note_off',
                    'channel': channel,
                    'note': note,
                    'timestamp': timestamp
                })

        except Exception as e:
            self.logger.warning(f"Error processing MIDI event: {e}")

    def _reset_midi_connection(self):
        """Reset MIDI connection safely"""
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None

            # Clear state
            with self._state_lock:
                self.cc_values.clear()
                self.note_states.clear()

            self.logger.info("MIDI connection reset")
        except Exception as e:
            self.logger.error(f"Error resetting MIDI connection: {e}")

    async def start_server(self):
        """Start WebSocket server with improved error handling and cleanup"""
        self.logger.info(f"Starting MIDI Bridge WebSocket server on port {self.websocket_port}")

        # Initialize async components
        self.loop = asyncio.get_running_loop()
        self.message_queue = asyncio.Queue()

        # Setup MIDI with fallback
        if not self.setup_midi_input():
            self.logger.warning("Failed to setup MIDI input, server will run without MIDI")

        self.running = True

        # Start MIDI processing thread
        midi_thread = threading.Thread(target=self.process_midi_messages, name="MIDI-Processor")
        midi_thread.daemon = True
        midi_thread.start()

        # Start message queue processor
        queue_task = asyncio.create_task(self.process_message_queue())

        try:
            # Start WebSocket server
            async with websockets.serve(
                self.register_client,
                "localhost",
                self.websocket_port,
                ping_interval=20,  # Keep connections alive
                ping_timeout=10,
                close_timeout=10
            ):
                self.logger.info(f"🎵 MIDI Bridge running on ws://localhost:{self.websocket_port}")
                self.logger.info("Ready to bridge MIDI data to web interface!")

                # Run until stopped
                await asyncio.Future()  # Run forever

        except KeyboardInterrupt:
            self.logger.info("Shutdown requested via KeyboardInterrupt")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            await self._cleanup(queue_task)

    async def _cleanup(self, queue_task):
        """Clean shutdown of all resources"""
        self.logger.info("Shutting down MIDI Bridge...")

        self.running = False

        # Stop queue processing
        if queue_task and not queue_task.done():
            queue_task.cancel()
            try:
                await queue_task
            except asyncio.CancelledError:
                pass

        # Close MIDI resources
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None
        except Exception as e:
            self.logger.warning(f"Error closing MIDI input: {e}")

        # Close pygame MIDI
        try:
            pygame.midi.quit()
            pygame.quit()
        except Exception as e:
            self.logger.warning(f"Error closing pygame: {e}")

        # Close remaining WebSocket connections
        if self.clients:
            self.logger.info(f"Closing {len(self.clients)} remaining connections")
            for client in list(self.clients):
                try:
                    await client.close()
                except Exception:
                    pass
            self.clients.clear()

        self.logger.info("MIDI Bridge shutdown complete")

def main():
    """Main entry point with proper logging setup"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('midi_bridge.log', mode='a')
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting MIDI Bridge...")

    try:
        bridge = MIDIBridge()
        asyncio.run(bridge.start_server())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()