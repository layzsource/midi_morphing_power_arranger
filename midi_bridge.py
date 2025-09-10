import asyncio
import websockets
import json
from pythonosc import udp_client

class MIDIBridge:
    """Bridge MIDI data between PySide6 app and web visualizer."""
    
    def __init__(self):
        self.osc_client = udp_client.SimpleUDPClient("127.0.0.1", 5005)
        self.websocket = None
        
    async def forward_to_web(self, note, velocity):
        """Forward MIDI data to web visualizer via WebSocket."""
        if self.websocket:
            data = json.dumps({
                'type': 'midi',
                'note': note,
                'velocity': velocity
            })
            await self.websocket.send(data)
    
    def forward_to_osc(self, note, velocity):
        """Forward MIDI data via OSC."""
        self.osc_client.send_message("/midi/note", [note, velocity])
