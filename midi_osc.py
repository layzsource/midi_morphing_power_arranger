"""
MIDI to OSC bridge and communication handling with multiple MIDI backend support.
"""

import logging
import threading
import time
from typing import Optional, List, Tuple
from PySide6.QtCore import QThread, Signal

from config import Config, MidiConstants
from exceptions import MidiConnectionError, OSCServerError

# Try to import OSC libraries (these should work)
try:
    from pythonosc import udp_client
    from pythonosc import dispatcher
    from pythonosc import osc_server
    OSC_AVAILABLE = True
except ImportError as e:
    OSC_AVAILABLE = False
    print(f"Warning: OSC libraries not available: {e}")

# Try multiple MIDI backends in order of preference
MIDI_BACKEND = None
MIDI_AVAILABLE = False

# First try rtmidi (most comprehensive but problematic on some systems)
try:
    import rtmidi
    from rtmidi.midiutil import open_midiinput
    MIDI_BACKEND = "rtmidi"
    MIDI_AVAILABLE = True
    print("Using rtmidi backend for MIDI")
except ImportError:
    pass

# Fallback to pygame (more reliable on many systems)
if not MIDI_AVAILABLE:
    try:
        import pygame
        import pygame.midi
        MIDI_BACKEND = "pygame"
        MIDI_AVAILABLE = True
        print("Using pygame backend for MIDI")
    except ImportError:
        pass

# Final fallback to mido (pure Python, works everywhere)
if not MIDI_AVAILABLE:
    try:
        import mido
        MIDI_BACKEND = "mido"
        MIDI_AVAILABLE = True
        print("Using mido backend for MIDI")
    except ImportError:
        pass

if not MIDI_AVAILABLE:
    print("Warning: No MIDI libraries available. MIDI functionality will be disabled.")
    print("To enable MIDI, install one of: pygame, mido, or rtmidi")

logger = logging.getLogger(__name__)

class MidiDevice:
    """Abstract MIDI device wrapper to handle different backends."""
    
    def __init__(self, port_name: str = None):
        self.port_name = port_name
        self.device = None
        self.callback = None
        self.backend = MIDI_BACKEND
        
    def open(self, callback=None) -> bool:
        """Open MIDI device with the available backend."""
        if not MIDI_AVAILABLE:
            logger.warning("No MIDI backend available")
            return False
            
        self.callback = callback
        
        try:
            if self.backend == "rtmidi":
                return self._open_rtmidi()
            elif self.backend == "pygame":
                return self._open_pygame()
            elif self.backend == "mido":
                return self._open_mido()
        except Exception as e:
            logger.error(f"Failed to open MIDI device with {self.backend}: {e}")
            return False
        
        return False
    
    def _open_rtmidi(self) -> bool:
        """Open device using rtmidi backend."""
        try:
            if self.port_name:
                self.device, actual_port = open_midiinput(self.port_name)
            else:
                # Try to open any available port
                midi_in = rtmidi.MidiIn()
                ports = midi_in.get_ports()
                if ports:
                    self.device, actual_port = open_midiinput(ports[0])
                    self.port_name = actual_port
                else:
                    return False
            
            if self.callback:
                self.device.set_callback(self._rtmidi_callback)
            
            logger.info(f"Opened MIDI device: {self.port_name}")
            return True
            
        except Exception as e:
            logger.error(f"rtmidi failed: {e}")
            return False
    
    def _open_pygame(self) -> bool:
        """Open device using pygame backend."""
        try:
            pygame.midi.init()
            
            # Find input device
            device_id = None
            device_count = pygame.midi.get_count()
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]  # 1 for input, 0 for output
                
                if is_input:
                    if self.port_name and self.port_name.lower() in name.lower():
                        device_id = i
                        self.port_name = name
                        break
                    elif not self.port_name and device_id is None:
                        device_id = i
                        self.port_name = name
            
            if device_id is not None:
                self.device = pygame.midi.Input(device_id)
                logger.info(f"Opened MIDI device: {self.port_name}")
                
                # Start polling thread for pygame
                if self.callback:
                    self._start_pygame_polling()
                
                return True
            else:
                logger.warning("No MIDI input devices found")
                return False
                
        except Exception as e:
            logger.error(f"pygame.midi failed: {e}")
            return False
    
    def _open_mido(self) -> bool:
        """Open device using mido backend."""
        try:
            ports = mido.get_input_names()
            
            if not ports:
                logger.warning("No MIDI input ports found")
                return False
            
            # Find matching port or use first available
            port_name = None
            if self.port_name:
                for port in ports:
                    if self.port_name.lower() in port.lower():
                        port_name = port
                        break
            
            if not port_name:
                port_name = ports[0]
            
            self.device = mido.open_input(port_name)
            self.port_name = port_name
            logger.info(f"Opened MIDI device: {self.port_name}")
            
            # Start polling thread for mido
            if self.callback:
                self._start_mido_polling()
            
            return True
            
        except Exception as e:
            logger.error(f"mido failed: {e}")
            return False
    
    def _rtmidi_callback(self, message, data=None):
        """Callback for rtmidi backend."""
        if self.callback:
            self.callback(message, data)
    
    def _start_pygame_polling(self):
        """Start polling thread for pygame backend."""
        def poll_pygame():
            while self.device and hasattr(self, '_polling_active') and self._polling_active:
                try:
                    if self.device.poll():
                        midi_events = self.device.read(10)
                        for event in midi_events:
                            midi_data = event[0]  # [status, data1, data2, data3]
                            timestamp = event[1]
                            
                            # Convert to rtmidi-like format
                            message = (midi_data[:3], timestamp)  # Take first 3 bytes
                            self.callback(message)
                    
                    time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                except Exception as e:
                    logger.error(f"Pygame polling error: {e}")
                    break
        
        self._polling_active = True
        self._polling_thread = threading.Thread(target=poll_pygame, daemon=True)
        self._polling_thread.start()
    
    def _start_mido_polling(self):
        """Start polling thread for mido backend."""
        def poll_mido():
            while self.device and hasattr(self, '_polling_active') and self._polling_active:
                try:
                    for msg in self.device.iter_pending():
                        # Convert mido message to rtmidi-like format
                        if hasattr(msg, 'bytes'):
                            midi_bytes = msg.bytes()
                            message = (list(midi_bytes), time.time())
                            self.callback(message)
                    
                    time.sleep(0.001)  # Small delay
                except Exception as e:
                    logger.error(f"Mido polling error: {e}")
                    break
        
        self._polling_active = True
        self._polling_thread = threading.Thread(target=poll_mido, daemon=True)
        self._polling_thread.start()
    
    def close(self):
        """Close the MIDI device."""
        try:
            if hasattr(self, '_polling_active'):
                self._polling_active = False
            
            if self.device:
                if self.backend == "rtmidi":
                    self.device.close_port()
                elif self.backend == "pygame":
                    self.device.close()
                    pygame.midi.quit()
                elif self.backend == "mido":
                    self.device.close()
                
                self.device = None
                logger.info("MIDI device closed")
                
        except Exception as e:
            logger.error(f"Error closing MIDI device: {e}")
    
    @staticmethod
    def list_devices() -> List[str]:
        """List available MIDI input devices."""
        devices = []
        
        if not MIDI_AVAILABLE:
            return devices
        
        try:
            if MIDI_BACKEND == "rtmidi":
                midi_in = rtmidi.MidiIn()
                devices = midi_in.get_ports()
            elif MIDI_BACKEND == "pygame":
                pygame.midi.init()
                device_count = pygame.midi.get_count()
                for i in range(device_count):
                    info = pygame.midi.get_device_info(i)
                    if info[2]:  # is_input
                        name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                        devices.append(name)
                pygame.midi.quit()
            elif MIDI_BACKEND == "mido":
                devices = mido.get_input_names()
                
        except Exception as e:
            logger.error(f"Error listing MIDI devices: {e}")
        
        return devices

class IntegratedMidiOscThread(QThread):
    """Integrated MIDI-OSC bridge thread with fallback support."""
    
    osc_message_signal = Signal(str, list)
    error_signal = Signal(str)
    status_signal = Signal(str)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.running = True
        
        # OSC components
        self.dispatcher = None
        self.server = None
        self.client = None
        self.server_thread = None
        
        # MIDI components
        self.midi_device = None

    def run(self):
        """Main thread execution."""
        try:
            if OSC_AVAILABLE:
                self._setup_osc()
                self._start_osc_server()
            else:
                self.error_signal.emit("OSC libraries not available")
                
            if MIDI_AVAILABLE:
                self._setup_midi()
            else:
                self.status_signal.emit("MIDI: Not available")
                
        except Exception as e:
            logger.error(f"Thread setup failed: {e}")
            self.error_signal.emit(f"Setup failed: {e}")

    def _setup_osc(self):
        """Setup OSC server and client with error handling."""
        if not OSC_AVAILABLE:
            raise OSCServerError("OSC libraries not available")
            
        try:
            self.dispatcher = dispatcher.Dispatcher()
            self.server = osc_server.ThreadingOSCUDPServer(
                (self.config.OSC_IP, self.config.OSC_PORT), 
                self.dispatcher
            )
            self.dispatcher.set_default_handler(self.default_handler)
            self.client = udp_client.SimpleUDPClient(self.config.OSC_IP, self.config.OSC_PORT)
            logger.info(f"✓ OSC setup complete on {self.config.OSC_IP}:{self.config.OSC_PORT}")
        except Exception as e:
            logger.error(f"OSC setup failed: {e}")
            raise OSCServerError(f"Failed to setup OSC: {e}")

    def _setup_midi(self):
        """Setup MIDI input with comprehensive error handling."""
        if not MIDI_AVAILABLE:
            logger.warning("MIDI not available")
            return
            
        try:
            self.midi_device = MidiDevice(self.config.MIDI_PORT)
            
            if self.midi_device.open(callback=self.midi_callback):
                logger.info(f"✓ Connected to MIDI: {self.midi_device.port_name} ({MIDI_BACKEND})")
                self.status_signal.emit(f"MIDI: {self.midi_device.port_name}")
            else:
                # Try to open any available device
                devices = MidiDevice.list_devices()
                if devices:
                    self.midi_device = MidiDevice(devices[0])
                    if self.midi_device.open(callback=self.midi_callback):
                        logger.info(f"✓ Connected to fallback MIDI: {self.midi_device.port_name}")
                        self.status_signal.emit(f"MIDI: {self.midi_device.port_name} (fallback)")
                    else:
                        self.status_signal.emit("MIDI: Connection failed")
                else:
                    self.status_signal.emit("MIDI: No devices found")
                    
        except Exception as e:
            logger.error(f"MIDI setup failed: {e}")
            self.error_signal.emit(f"MIDI error: {e}")

    def _start_osc_server(self):
        """Start OSC server in separate thread."""
        if not OSC_AVAILABLE or not self.server:
            return
            
        try:
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.info("✓ OSC server started")
            self.status_signal.emit(f"OSC: {self.config.OSC_IP}:{self.config.OSC_PORT}")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
            raise OSCServerError(f"Server start failed: {e}")
    
    def default_handler(self, address, *args):
        """Handle incoming OSC messages."""
        try:
            self.osc_message_signal.emit(address, list(args))
        except Exception as e:
            logger.error(f"OSC message handling failed: {e}")

    def midi_callback(self, message, data=None):
        """Process incoming MIDI messages and convert to OSC."""
        if not OSC_AVAILABLE or not self.client:
            return
            
        try:
            midi_message, _ = message
            if not midi_message:
                return

            # Handle different message lengths
            if len(midi_message) < 2:
                return
                
            midi_status = midi_message[0]
            
            # CC Message
            if (MidiConstants.CC_START <= midi_status <= MidiConstants.CC_END and 
                len(midi_message) >= 3):
                cc_number = midi_message[1]
                cc_value = midi_message[2]
                osc_address = f"/midi/cc/{cc_number}"
                high_res_value = cc_value / MidiConstants.MAX_VALUE
                self.client.send_message(osc_address, [high_res_value])
            
            # Note On/Off Message
            elif (MidiConstants.NOTE_OFF_START <= midi_status <= MidiConstants.NOTE_ON_END and 
                  len(midi_message) >= 3):
                note = midi_message[1]
                velocity = midi_message[2]
                osc_address = f"/midi/note/{note}"
                high_res_value = velocity / MidiConstants.MAX_VALUE
                self.client.send_message(osc_address, [high_res_value])
                
        except Exception as e:
            logger.error(f"MIDI callback error: {e}")

    def stop(self):
        """Cleanly stop all threads and connections."""
        try:
            self.running = False
            
            if self.midi_device:
                self.midi_device.close()
                logger.info("MIDI device closed")
            
            if self.server:
                self.server.shutdown()
                logger.info("OSC server stopped")
            
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join(timeout=1.0)
            
            self.quit()
        except Exception as e:
            logger.error(f"Error during thread shutdown: {e}")

    def reconnect_midi(self):
        """Attempt to reconnect MIDI device."""
        if not MIDI_AVAILABLE:
            return False
            
        try:
            if self.midi_device:
                self.midi_device.close()
            
            self._setup_midi()
            return self.midi_device is not None and self.midi_device.device is not None
            
        except Exception as e:
            logger.error(f"MIDI reconnection failed: {e}")
            return False

    def get_available_devices(self) -> List[str]:
        """Get list of available MIDI devices."""
        if not MIDI_AVAILABLE:
            return []
        return MidiDevice.list_devices()

    def get_status(self) -> dict:
        """Get current connection status."""
        status = {
            'midi_available': MIDI_AVAILABLE,
            'midi_backend': MIDI_BACKEND,
            'osc_available': OSC_AVAILABLE,
            'midi_connected': False,
            'midi_device_name': None,
            'osc_running': False
        }
        
        if self.midi_device and self.midi_device.device:
            status['midi_connected'] = True
            status['midi_device_name'] = self.midi_device.port_name
            
        if self.server:
            status['osc_running'] = True
            
        return status
