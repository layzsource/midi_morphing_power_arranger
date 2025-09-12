#!/usr/bin/env python3
"""
MIDI Handler module for the morphing visualizer.
Handles MIDI input and converts to application events.
"""

import time
import threading
import pygame
import pygame.midi
from PySide6.QtCore import QObject, Signal

class MidiHandler(QObject):
    """Basic MIDI handler using pygame.midi"""
    
    # Signals for MIDI events
    note_on = Signal(int, int)  # note, velocity
    note_off = Signal(int)      # note
    control_change = Signal(int, int)  # control, value
    
    def __init__(self):
        super().__init__()
        self.midi_input = None
        self.running = False
        self.thread = None
        self.midi_initialized = False
        
    def initialize(self):
        """Initialize MIDI system."""
        try:
            if not self.midi_initialized:
                pygame.init()
                pygame.midi.init()
                self.midi_initialized = True
                print("✓ MIDI system initialized")
            return True
        except Exception as e:
            print(f"✗ Failed to initialize MIDI: {e}")
            return False
    
    def find_device(self, preferred_name=None):
        """Find a MIDI input device."""
        if not self.midi_initialized:
            if not self.initialize():
                return None
        
        try:
            device_count = pygame.midi.get_count()
            print(f"Found {device_count} MIDI devices:")
            
            # List all devices
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]
                is_output = info[3]
                is_opened = info[4]
                
                if is_input:
                    print(f"  [{i}] {name} (Input)")
                    
                    # If preferred name matches, return this device
                    if preferred_name and preferred_name.lower() in name.lower():
                        return i
            
            # If no preferred device or not found, return first available input
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                if info[2]:  # is_input
                    return i
            
            return None
            
        except Exception as e:
            print(f"Error finding MIDI device: {e}")
            return None
    
    def start(self, device_name=None):
        """Start MIDI handling."""
        if not self.midi_initialized:
            if not self.initialize():
                return False
        
        try:
            # Find device
            device_id = self.find_device(device_name)
            
            if device_id is None:
                print("✗ No MIDI input devices found")
                return False
            
            # Open MIDI input
            self.midi_input = pygame.midi.Input(device_id)
            
            # Get device info for logging
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"✓ Connected to MIDI device: {device_name}")
            
            # Start polling thread
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to start MIDI: {e}")
            self._cleanup_midi()
            return False
    
    def _midi_loop(self):
        """Main MIDI polling loop."""
        while self.running and self.midi_input:
            try:
                # Check if MIDI system is still initialized
                if not self.midi_initialized:
                    break
                
                # Poll for MIDI events
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                # Small delay to prevent CPU hogging
                time.sleep(0.001)
                
            except Exception as e:
                print(f"MIDI polling error: {e}")
                break
    
    def _process_midi_event(self, midi_data):
        """Process a single MIDI event."""
        if len(midi_data) < 3:
            return
        
        status, data1, data2 = midi_data[:3]
        message_type = status & 0xF0
        channel = status & 0x0F
        
        # Note On (144-159)
        if message_type == 0x90:
            if data2 > 0:
                self.note_on.emit(data1, data2)
            else:
                # Note on with velocity 0 is treated as note off
                self.note_off.emit(data1)
        
        # Note Off (128-143)
        elif message_type == 0x80:
            self.note_off.emit(data1)
        
        # Control Change (176-191)
        elif message_type == 0xB0:
            self.control_change.emit(data1, data2)
    
    def _cleanup_midi(self):
        """Clean up MIDI resources."""
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None
        except Exception as e:
            print(f"Error closing MIDI input: {e}")
        
        try:
            if self.midi_initialized:
                pygame.midi.quit()
                self.midi_initialized = False
        except Exception as e:
            print(f"Error quitting pygame.midi: {e}")
    
    def stop(self):
        """Stop MIDI handler safely."""
        print("Stopping MIDI handler...")
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Cleanup MIDI resources
        self._cleanup_midi()
        print("✓ MIDI handler stopped")
    
    def get_device_list(self):
        """Get list of available MIDI devices."""
        devices = []
        
        if not self.midi_initialized:
            if not self.initialize():
                return devices
        
        try:
            device_count = pygame.midi.get_count()
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]
                
                if is_input:
                    devices.append({
                        'id': i,
                        'name': name,
                        'type': 'input'
                    })
            
        except Exception as e:
            print(f"Error getting device list: {e}")
        
        return devices


# Test function
def test_midi_handler():
    """Test MIDI handler functionality."""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    handler = MidiHandler()
    
    # Connect to signals for testing
    handler.note_on.connect(lambda n, v: print(f"Note ON: {n}, velocity: {v}"))
    handler.note_off.connect(lambda n: print(f"Note OFF: {n}"))
    handler.control_change.connect(lambda c, v: print(f"CC: {c} = {v}"))
    
    # List devices
    devices = handler.get_device_list()
    print(f"\nAvailable MIDI devices:")
    for device in devices:
        print(f"  {device['name']}")
    
    # Start handler
    if handler.start():
        print("\nMIDI handler running. Press Ctrl+C to stop...")
        try:
            app.exec()
        except KeyboardInterrupt:
            pass
    else:
        print("Failed to start MIDI handler")
    
    handler.stop()


if __name__ == "__main__":
    test_midi_handler()
