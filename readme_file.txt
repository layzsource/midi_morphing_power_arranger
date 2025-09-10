# MIDI to OSC Morphing Interface

A real-time audio-visual morphing system that combines MIDI input, OSC messaging, 3D mesh visualization, and audio analysis for interactive performance art and live shows.

## Features

### Core Functionality
- **Real-time 3D mesh morphing** between geometric shapes (sphere, cone, cube, torus, icosahedron)
- **MIDI input processing** with automatic device detection and fallback
- **OSC message routing** for external application integration
- **Real-time audio analysis** with onset detection and spectral feature extraction
- **Dynamic lighting system** with intelligent management and multiple removal strategies

### Performance & Monitoring
- **Comprehensive performance profiling** with real-time metrics
- **Memory and CPU monitoring** with configurable thresholds
- **FPS tracking and optimization** with automatic performance warnings
- **Debounced rendering** to maintain smooth frame rates
- **Intelligent light management** with configurable removal strategies

### Audio-Visual Integration
- **Pitch-to-color mapping** using HSV color space
- **Amplitude-to-intensity mapping** for dynamic lighting
- **Spectral feature extraction** (centroid, rolloff, bandwidth)
- **Audio-driven morphing** with configurable sensitivity
- **Onset detection** for reactive lighting effects

## Project Structure

```
morphing_interface/
├── main.py                 # Application entry point
├── __init__.py            # Package initialization
├── config.py              # Configuration management
├── exceptions.py          # Custom exceptions
├── profiler.py           # Performance profiling system
├── geometry.py           # Mesh creation and manipulation
├── audio.py              # Real-time audio analysis
├── midi_osc.py           # MIDI to OSC bridge
├── dialogs.py            # UI configuration dialogs
├── main_window.py        # Main application window
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Installation

1. **Clone or download** the project files
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install system audio dependencies** (platform-specific):
   - **Windows:** Usually included with Python
   - **macOS:** Install PortAudio: `brew install portaudio`
   - **Linux:** Install ALSA and PortAudio: `sudo apt-get install libasound2-dev portaudio19-dev`

## Usage

### Basic Usage
```bash
python main.py
```

### Command Line Options
```bash
# Disable audio analysis
python main.py --no-audio

# Set specific MIDI port
python main.py --midi-port "Your MIDI Device"

# Set OSC port
python main.py --osc-port 5006

# Load custom configuration
python main.py --config my_config.json

# Set log level
python main.py --log-level DEBUG
```

## Configuration

The application provides a comprehensive settings dialog accessible through the main window. Settings are automatically saved and restored between sessions.

### Key Configuration Areas

**MIDI/OSC Settings:**
- MIDI device selection with automatic fallback
- OSC IP address and port configuration
- Connection status monitoring

**Visualization Settings:**
- Mesh resolution (affects detail vs performance)
- Material properties (metallic, roughness)
- Color schemes and HSV mapping

**Performance Tuning:**
- Render debouncing for smooth animation
- Light cleanup intervals
- Memory and CPU monitoring thresholds

**Audio Analysis:**
- Sample rate and buffer size configuration
- Onset detection sensitivity
- Frequency range filtering
- Audio-to-visual mapping parameters

## Performance Optimization

The application includes sophisticated performance monitoring:

- **Real-time FPS tracking** with color-coded warnings
- **Memory usage monitoring** with automatic cleanup
- **CPU utilization tracking** with performance alerts
- **Profiling system** with detailed timing metrics
- **Export functionality** for performance reports

## MIDI Integration

Supports standard MIDI messages:
- **Note On/Off:** Creates/removes lights with velocity-based intensity
- **Control Change:** Controls morphing blend amount (CC#1)
- **Automatic device detection** with graceful fallback
- **Hot-plugging support** with reconnection functionality

## Audio Features

Real-time audio analysis provides:
- **Spectral centroid** for pitch estimation
- **RMS amplitude** for volume detection
- **Onset detection** for rhythmic responsiveness
- **Spectral rolloff** for brightness analysis
- **Configurable frequency ranges** for targeted analysis

## Troubleshooting

### Common Issues

**No MIDI devices detected:**
- Ensure MIDI device is connected and powered on
- Check device drivers are installed
- Try reconnecting the device
- Use the "Reconnect MIDI" button in the interface

**Audio not working:**
- Check system audio permissions
- Verify microphone/audio input is working
- Try different sample rates in settings
- Check the audio device selection

**Performance issues:**
- Lower mesh resolution in settings
- Reduce maximum light count
- Increase render debounce time
- Monitor performance dialog for bottlenecks

**OSC connection issues:**
- Verify IP address and port settings
- Check firewall settings
- Ensure no other applications are using the same port

### Log Files

The application creates detailed log files (`morphing_visualizer.log`) for troubleshooting. Set log level to DEBUG for maximum detail.

## Development

### Code Architecture

The codebase follows a modular design with clear separation of concerns:

- **Config management** with persistent settings
- **Thread-based architecture** for responsive UI
- **Comprehensive error handling** with graceful degradation
- **Performance profiling** with decorator-based instrumentation
- **Signal/slot communication** between components

### Adding New Features

1. **New geometric shapes:** Add to `geometry.py` mesh creation functions
2. **Audio features:** Extend `audio.py` analysis methods
3. **MIDI mappings:** Modify `midi_osc.py` message handling
4. **UI elements:** Add to appropriate dialog in `dialogs.py`

### Testing

The modular structure facilitates unit testing:
```bash
# Install test dependencies
pip install pytest pytest-qt

# Run tests (when implemented)
pytest tests/
```

## License

This project is provided as-is for educational and artistic purposes. Please respect the licenses of all dependencies.

## Contributing

When contributing:
1. Follow the existing code style and structure
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Test with various MIDI devices and audio inputs
5. Ensure performance profiling covers new code paths

## Technical Notes

### Dependencies
- **PySide6:** Cross-platform GUI framework
- **PyVista:** 3D visualization and mesh processing
- **PyAudio:** Real-time audio input/output
- **python-rtmidi:** MIDI device communication
- **python-osc:** OSC message handling
- **librosa:** Audio signal processing
- **psutil:** System resource monitoring

### Performance Considerations
- The application uses multi-threading for audio, MIDI, and UI responsiveness
- Mesh morphing is optimized with debounced rendering
- Light management prevents memory leaks with intelligent cleanup
- Performance profiling helps identify bottlenecks in real-time