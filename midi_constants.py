"""
MIDI Constants and Utilities

Defines standard MIDI constants, message types, and utility functions
for MIDI processing in the morphing interface.
"""

class MidiConstants:
    """Standard MIDI constants and message types."""
    
    # MIDI Value Ranges
    MIN_VALUE = 0
    MAX_VALUE = 127
    
    # Note ranges
    MIN_NOTE = 0
    MAX_NOTE = 127
    
    # Velocity ranges
    MIN_VELOCITY = 0
    MAX_VELOCITY = 127
    
    # Control Change ranges
    MIN_CC = 0
    MAX_CC = 127
    
    # Channel ranges (0-based internally, 1-based for display)
    MIN_CHANNEL = 0
    MAX_CHANNEL = 15
    
    # Standard MIDI Message Types (Status Bytes)
    # Note Off: 128-143 (0x80-0x8F)
    NOTE_OFF_START = 128
    NOTE_OFF_END = 143
    
    # Note On: 144-159 (0x90-0x9F)
    NOTE_ON_START = 144
    NOTE_ON_END = 159
    
    # Polyphonic Key Pressure: 160-175 (0xA0-0xAF)
    POLY_PRESSURE_START = 160
    POLY_PRESSURE_END = 175
    
    # Control Change: 176-191 (0xB0-0xBF)
    CC_START = 176
    CC_END = 191
    
    # Program Change: 192-207 (0xC0-0xCF)
    PROGRAM_CHANGE_START = 192
    PROGRAM_CHANGE_END = 207
    
    # Channel Pressure: 208-223 (0xD0-0xDF)
    CHANNEL_PRESSURE_START = 208
    CHANNEL_PRESSURE_END = 223
    
    # Pitch Bend: 224-239 (0xE0-0xEF)
    PITCH_BEND_START = 224
    PITCH_BEND_END = 239
    
    # System Messages: 240-255 (0xF0-0xFF)
    SYSTEM_START = 240
    SYSTEM_END = 255
    
    # Common Control Change Numbers
    class CC:
        """Common Control Change (CC) numbers."""
        BANK_SELECT_MSB = 0
        MODULATION_WHEEL = 1
        BREATH_CONTROLLER = 2
        FOOT_CONTROLLER = 4
        PORTAMENTO_TIME = 5
        DATA_ENTRY_MSB = 6
        VOLUME = 7
        BALANCE = 8
        PAN = 10
        EXPRESSION = 11
        EFFECT_CONTROL_1 = 12
        EFFECT_CONTROL_2 = 13
        GENERAL_PURPOSE_1 = 16
        GENERAL_PURPOSE_2 = 17
        GENERAL_PURPOSE_3 = 18
        GENERAL_PURPOSE_4 = 19
        BANK_SELECT_LSB = 32
        DATA_ENTRY_LSB = 38
        SUSTAIN_PEDAL = 64
        PORTAMENTO = 65
        SOSTENUTO = 66
        SOFT_PEDAL = 67
        LEGATO = 68
        HOLD_2 = 69
        SOUND_VARIATION = 70
        HARMONIC_CONTENT = 71
        RELEASE_TIME = 72
        ATTACK_TIME = 73
        BRIGHTNESS = 74
        DECAY_TIME = 75
        VIBRATO_RATE = 76
        VIBRATO_DEPTH = 77
        VIBRATO_DELAY = 78
        GENERAL_PURPOSE_5 = 80
        GENERAL_PURPOSE_6 = 81
        GENERAL_PURPOSE_7 = 82
        GENERAL_PURPOSE_8 = 83
        PORTAMENTO_CONTROL = 84
        REVERB_SEND = 91
        TREMOLO_DEPTH = 92
        CHORUS_SEND = 93
        CELESTE_DEPTH = 94
        PHASER_DEPTH = 95
        DATA_INCREMENT = 96
        DATA_DECREMENT = 97
        NRPN_LSB = 98
        NRPN_MSB = 99
        RPN_LSB = 100
        RPN_MSB = 101
        ALL_SOUND_OFF = 120
        RESET_ALL_CONTROLLERS = 121
        LOCAL_CONTROL = 122
        ALL_NOTES_OFF = 123
        OMNI_MODE_OFF = 124
        OMNI_MODE_ON = 125
        MONO_MODE_ON = 126
        POLY_MODE_ON = 127
    
    # Note Names
    NOTE_NAMES = [
        'C', 'C#', 'D', 'D#', 'E', 'F', 
        'F#', 'G', 'G#', 'A', 'A#', 'B'
    ]
    
    # Common Note Ranges for Different Instruments
    class NoteRanges:
        """Common note ranges for different instrument types."""
        PIANO_MIN = 21  # A0
        PIANO_MAX = 108  # C8
        
        GUITAR_MIN = 40  # E2
        GUITAR_MAX = 88  # E6
        
        BASS_MIN = 28   # E1
        BASS_MAX = 67   # G4
        
        VOCAL_SOPRANO_MIN = 60  # C4
        VOCAL_SOPRANO_MAX = 84  # C6
        
        VOCAL_ALTO_MIN = 55  # G3
        VOCAL_ALTO_MAX = 79  # G5
        
        VOCAL_TENOR_MIN = 48  # C3
        VOCAL_TENOR_MAX = 72  # C5
        
        VOCAL_BASS_MIN = 41  # F2
        VOCAL_BASS_MAX = 65  # F4
        
        DRUMS_MIN = 35  # Kick drum (typical)
        DRUMS_MAX = 81  # Open triangle (typical)
    
    @staticmethod
    def note_to_name(note_number):
        """Convert MIDI note number to note name with octave.
        
        Args:
            note_number (int): MIDI note number (0-127)
            
        Returns:
            str: Note name with octave (e.g., 'C4', 'A#5')
        """
        if not (0 <= note_number <= 127):
            return f"Invalid({note_number})"
        
        octave = (note_number // 12) - 1
        note_name = MidiConstants.NOTE_NAMES[note_number % 12]
        return f"{note_name}{octave}"
    
    @staticmethod
    def name_to_note(note_name):
        """Convert note name to MIDI note number.
        
        Args:
            note_name (str): Note name with octave (e.g., 'C4', 'A#5')
            
        Returns:
            int: MIDI note number (0-127) or None if invalid
        """
        try:
            # Parse note name and octave
            if len(note_name) < 2:
                return None
            
            # Handle sharp/flat notation
            if '#' in note_name or 'b' in note_name:
                note_part = note_name[:-1]
                octave_part = note_name[-1]
            else:
                note_part = note_name[:-1]
                octave_part = note_name[-1]
            
            # Convert flat to sharp
            if 'b' in note_part:
                note_part = note_part.replace('b', '')
                # Convert flat to equivalent sharp
                flat_to_sharp = {
                    'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 
                    'Ab': 'G#', 'Bb': 'A#'
                }
                note_part = flat_to_sharp.get(note_part + 'b', note_part)
            
            # Find note in the chromatic scale
            if note_part not in MidiConstants.NOTE_NAMES:
                return None
            
            note_index = MidiConstants.NOTE_NAMES.index(note_part)
            octave = int(octave_part)
            
            # Calculate MIDI note number
            midi_note = (octave + 1) * 12 + note_index
            
            # Validate range
            if 0 <= midi_note <= 127:
                return midi_note
            else:
                return None
                
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def note_to_frequency(note_number):
        """Convert MIDI note number to frequency in Hz.
        
        Args:
            note_number (int): MIDI note number (0-127)
            
        Returns:
            float: Frequency in Hz
        """
        # A4 (note 69) = 440 Hz
        return 440.0 * (2.0 ** ((note_number - 69) / 12.0))
    
    @staticmethod
    def frequency_to_note(frequency):
        """Convert frequency in Hz to nearest MIDI note number.
        
        Args:
            frequency (float): Frequency in Hz
            
        Returns:
            int: Nearest MIDI note number (0-127)
        """
        import math
        # A4 (note 69) = 440 Hz
        note_number = 69 + 12 * math.log2(frequency / 440.0)
        return max(0, min(127, round(note_number)))
    
    @staticmethod
    def is_note_on(status_byte):
        """Check if status byte represents a Note On message.
        
        Args:
            status_byte (int): MIDI status byte
            
        Returns:
            bool: True if Note On message
        """
        return MidiConstants.NOTE_ON_START <= status_byte <= MidiConstants.NOTE_ON_END
    
    @staticmethod
    def is_note_off(status_byte):
        """Check if status byte represents a Note Off message.
        
        Args:
            status_byte (int): MIDI status byte
            
        Returns:
            bool: True if Note Off message
        """
        return MidiConstants.NOTE_OFF_START <= status_byte <= MidiConstants.NOTE_OFF_END
    
    @staticmethod
    def is_control_change(status_byte):
        """Check if status byte represents a Control Change message.
        
        Args:
            status_byte (int): MIDI status byte
            
        Returns:
            bool: True if Control Change message
        """
        return MidiConstants.CC_START <= status_byte <= MidiConstants.CC_END
    
    @staticmethod
    def get_channel(status_byte):
        """Extract channel number from status byte.
        
        Args:
            status_byte (int): MIDI status byte
            
        Returns:
            int: Channel number (0-15)
        """
        return status_byte & 0x0F
    
    @staticmethod
    def get_message_type(status_byte):
        """Get human-readable message type from status byte.
        
        Args:
            status_byte (int): MIDI status byte
            
        Returns:
            str: Message type description
        """
        if MidiConstants.is_note_off(status_byte):
            return "Note Off"
        elif MidiConstants.is_note_on(status_byte):
            return "Note On"
        elif MidiConstants.POLY_PRESSURE_START <= status_byte <= MidiConstants.POLY_PRESSURE_END:
            return "Polyphonic Pressure"
        elif MidiConstants.is_control_change(status_byte):
            return "Control Change"
        elif MidiConstants.PROGRAM_CHANGE_START <= status_byte <= MidiConstants.PROGRAM_CHANGE_END:
            return "Program Change"
        elif MidiConstants.CHANNEL_PRESSURE_START <= status_byte <= MidiConstants.CHANNEL_PRESSURE_END:
            return "Channel Pressure"
        elif MidiConstants.PITCH_BEND_START <= status_byte <= MidiConstants.PITCH_BEND_END:
            return "Pitch Bend"
        elif MidiConstants.SYSTEM_START <= status_byte <= MidiConstants.SYSTEM_END:
            return "System Message"
        else:
            return f"Unknown ({status_byte})"
    
    @staticmethod
    def velocity_to_amplitude(velocity):
        """Convert MIDI velocity to normalized amplitude (0.0-1.0).
        
        Args:
            velocity (int): MIDI velocity (0-127)
            
        Returns:
            float: Normalized amplitude (0.0-1.0)
        """
        return velocity / 127.0
    
    @staticmethod
    def amplitude_to_velocity(amplitude):
        """Convert normalized amplitude to MIDI velocity.
        
        Args:
            amplitude (float): Normalized amplitude (0.0-1.0)
            
        Returns:
            int: MIDI velocity (0-127)
        """
        return max(0, min(127, round(amplitude * 127)))
    
    @staticmethod
    def cc_value_to_normalized(cc_value):
        """Convert CC value to normalized range (0.0-1.0).
        
        Args:
            cc_value (int): CC value (0-127)
            
        Returns:
            float: Normalized value (0.0-1.0)
        """
        return cc_value / 127.0
    
    @staticmethod
    def normalized_to_cc_value(normalized_value):
        """Convert normalized value to CC value.
        
        Args:
            normalized_value (float): Normalized value (0.0-1.0)
            
        Returns:
            int: CC value (0-127)
        """
        return max(0, min(127, round(normalized_value * 127)))


# Utility functions for common MIDI operations
def create_note_on(channel, note, velocity):
    """Create a Note On MIDI message.
    
    Args:
        channel (int): MIDI channel (0-15)
        note (int): Note number (0-127)
        velocity (int): Velocity (0-127)
        
    Returns:
        list: MIDI message bytes [status, note, velocity]
    """
    status = MidiConstants.NOTE_ON_START + (channel & 0x0F)
    return [status, note & 0x7F, velocity & 0x7F]


def create_note_off(channel, note, velocity=64):
    """Create a Note Off MIDI message.
    
    Args:
        channel (int): MIDI channel (0-15)
        note (int): Note number (0-127)
        velocity (int): Release velocity (0-127)
        
    Returns:
        list: MIDI message bytes [status, note, velocity]
    """
    status = MidiConstants.NOTE_OFF_START + (channel & 0x0F)
    return [status, note & 0x7F, velocity & 0x7F]


def create_control_change(channel, cc_number, value):
    """Create a Control Change MIDI message.
    
    Args:
        channel (int): MIDI channel (0-15)
        cc_number (int): CC number (0-127)
        value (int): CC value (0-127)
        
    Returns:
        list: MIDI message bytes [status, cc_number, value]
    """
    status = MidiConstants.CC_START + (channel & 0x0F)
    return [status, cc_number & 0x7F, value & 0x7F]


# Export main class
__all__ = ['MidiConstants', 'create_note_on', 'create_note_off', 'create_control_change']
