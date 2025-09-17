# 🎵 MMPA Audio-Visual Morphing System - Complete Usage Guide

**Version**: Production Release
**Date**: September 2025
**System**: Musical/Media Processing Architecture (MMPA)

---

## 📖 Table of Contents

1. [Quick Start](#-quick-start)
2. [Production Versions](#-production-versions)
3. [System Requirements](#-system-requirements)
4. [Installation](#-installation)
5. [Hardware Setup](#-hardware-setup)
6. [Usage Instructions](#-usage-instructions)
7. [Advanced Features](#-advanced-features)
8. [Troubleshooting](#-troubleshooting)
9. [Performance Optimization](#-performance-optimization)
10. [Professional Applications](#-professional-applications)

---

## 🚀 Quick Start

### 1. Choose Your Version
- **Light Version** → Everyday use, basic hardware
- **Standard Version** → Most users, balanced performance
- **Pro Version** → Professional use, high-end hardware

### 2. Run Your Version
```bash
# Light Version (30 FPS, basic features)
python3 mmpa_light.py

# Standard Version (45 FPS, full features)
python3 mmpa_standard.py

# Pro Version (60+ FPS, maximum quality)
python3 mmpa_pro.py
```

### 3. Connect Equipment
- **MIDI**: Connect MPK Mini or compatible controller
- **Audio**: Configure BlackHole for system audio capture
- **Start Playing**: Watch visuals respond to your music!

---

## 📦 Production Versions

### ⚡ Light Version (`mmpa_light.py`)
**Perfect for everyday use and basic hardware**

#### Features:
- ✅ 30 FPS performance target
- ✅ 6 core geometric shapes
- ✅ MIDI integration (MPK Mini support)
- ✅ Basic morphing system
- ✅ Minimal CPU usage (<20%)
- ✅ Fast startup (<2 seconds)

#### Best For:
- Basic laptops with integrated graphics
- Learning and experimentation
- Everyday music listening enhancement
- Systems with limited resources

#### What's Included:
- Sphere, Cube, Torus, Pyramid, Spiral, Star shapes
- Simple rainbow coloring
- MPK Mini MIDI control
- 200-point shape resolution

---

### 🎯 Standard Version (`mmpa_standard.py`)
**Recommended for most users - balanced performance**

#### Features:
- ✅ 45 FPS performance target
- ✅ 9 enhanced geometric shapes
- ✅ Full musical intelligence system (throttled)
- ✅ Multi-layer morphing (3 layers)
- ✅ Audio-reactive scaling & breathing
- ✅ Advanced particle physics
- ✅ Professional preset management
- ✅ Performance recording system

#### Best For:
- Modern computers with dedicated graphics
- Music production and composition
- Live performance setup
- Educational applications

#### Advanced Features:
- Real-time genre detection
- Key signature analysis
- Timeline automation
- HSV color space transitions
- Gravitational particle physics

---

### 🚀 Pro Version (`mmpa_pro.py`)
**Professional-grade for high-end systems**

#### Features:
- ✅ 60+ FPS maximum performance
- ✅ 9 professional geometric shapes
- ✅ Maximum musical intelligence (no throttling)
- ✅ Multi-layer morphing (up to 7 layers)
- ✅ Ultra-high resolution (2000+ points)
- ✅ Professional particle trails (25-point)
- ✅ Advanced color science
- ✅ Real-time performance monitoring

#### Best For:
- High-end workstations
- Professional concerts and installations
- Studio recording environments
- Broadcast and streaming
- Research applications

#### Professional Features:
- Golden ratio geometry (dodecahedron, icosahedron)
- Klein bottles and Möbius strips
- Professional-grade OpenGL rendering
- Advanced harmonic analysis
- Enterprise-grade performance monitoring

---

## 💻 System Requirements

### Minimum Requirements (Light Version)
- **OS**: macOS 10.14+ / Windows 10+ / Linux
- **Python**: 3.8+
- **RAM**: 4GB
- **Graphics**: Integrated graphics
- **CPU**: Dual-core 2.0GHz+

### Recommended (Standard Version)
- **OS**: macOS 11+ / Windows 11+ / Ubuntu 20.04+
- **Python**: 3.9+
- **RAM**: 8GB+
- **Graphics**: Dedicated graphics card
- **CPU**: Quad-core 2.5GHz+
- **Audio**: Dedicated audio interface

### Professional (Pro Version)
- **OS**: Latest macOS / Windows 11 Pro / Ubuntu 22.04+
- **Python**: 3.10+
- **RAM**: 16GB+
- **Graphics**: High-end dedicated GPU
- **CPU**: 8+ cores, 3.0GHz+
- **Audio**: Professional audio interface
- **Storage**: SSD recommended

---

## 🔧 Installation

### 1. Install Python Dependencies
```bash
pip install PySide6 numpy PyOpenGL librosa sounddevice pyaudio python-rtmidi
```

### 2. Install Audio Backend
#### macOS:
```bash
# Install BlackHole for system audio capture
brew install blackhole-2ch
```

#### Windows:
```bash
# Install ASIO drivers and VB-Cable
# Download from: https://vb-audio.com/Cable/
```

#### Linux:
```bash
# Install JACK and PulseAudio
sudo apt install jackd2 pulseaudio-dev
```

### 3. Download MMPA System
```bash
# Download the appropriate version files:
# - mmpa_light.py (Light Version)
# - mmpa_standard.py (Standard Version)
# - mmpa_pro.py (Pro Version)
# - mmpa_signal_framework.py (Core framework)
# - mmpa_midi_processor.py (MIDI processing)
# - mmpa_enhanced_audio_processor.py (Audio processing)
```

---

## 🎹 Hardware Setup

### MIDI Controller Setup
1. **Connect MPK Mini** (or compatible MIDI controller)
2. **Verify Connection**:
   ```bash
   python3 -c "import rtmidi; print(rtmidi.MidiIn().get_ports())"
   ```
3. **Test in MMPA**: Keys should trigger visual morphing

### Audio Setup
#### macOS with BlackHole:
1. **Install BlackHole 2ch** from the official website
2. **Configure Audio MIDI Setup**:
   - Open Audio MIDI Setup
   - Create Multi-Output Device
   - Include BlackHole 2ch + your speakers
3. **Set System Output** to Multi-Output Device
4. **Launch MMPA**: Should detect BlackHole automatically

#### Professional Audio Interface:
1. **Connect your audio interface** (Focusrite, RME, etc.)
2. **Configure routing** to send system audio to MMPA
3. **Test audio detection** in your chosen MMPA version

---

## 📱 Usage Instructions

### Basic Operation (All Versions)

#### 1. Launch Application
```bash
python3 mmpa_standard.py  # Example: Standard Version
```

#### 2. Main Interface
- **Visualization Area** (75%): Real-time morphing display
- **Control Panel** (25%): Settings and configuration

#### 3. Shape Selection
- **Shape A Dropdown**: Primary morphing shape
- **Shape B Dropdown**: Secondary morphing shape
- **Auto-morphing**: Shapes blend automatically with music

#### 4. Musical Control
- **Play music** through your system
- **Use MIDI controller** for direct interaction
- **Watch visuals** adapt to musical content

### Standard/Pro Version Advanced Controls

#### Preset Management
1. **Select Preset**: Choose from built-in professional presets
2. **Custom Configuration**: Adjust shapes, colors, effects
3. **Save Settings**: Create your own presets

#### Musical Intelligence Window
- **Real-time Analysis**: Genre, key signature, chord progression
- **Visual Feedback**: Color-coded musical information
- **Performance Data**: Frame rate and processing statistics

#### Timeline Automation
1. **Load Timeline**: Import automation sequences
2. **Playback Control**: Start/stop automated visual shows
3. **Custom Sequences**: Create your own timeline events

---

## 🎨 Advanced Features

### Musical Intelligence System (Standard/Pro)
- **Genre Detection**: Jazz, Classical, Rock, Electronic, Folk, Blues, Pop
- **Key Signature Analysis**: Real-time detection of musical keys
- **Chord Progression Tracking**: Harmonic structure visualization
- **Adaptive Visuals**: Genre-appropriate colors and effects

### Enhanced Geometric Library
#### Basic Shapes (All Versions):
- **Sphere**: Perfect spherical distribution
- **Cube**: Tessellated cubic forms
- **Torus**: Donut-shaped geometry

#### Advanced Shapes (Standard/Pro):
- **Dodecahedron**: 12-sided golden ratio geometry
- **Icosahedron**: 20-sided perfect polyhedron
- **Klein Bottle**: Non-orientable mathematical surface
- **Möbius Strip**: Single-sided topological form
- **Helix**: Three-dimensional spiral
- **Octahedron**: 8-sided bipyramidal form

### Multi-layer Morphing System
- **Layer Count**: 3 layers (Standard), up to 7 layers (Pro)
- **Phase Shifts**: Each layer morphs at different rates
- **Alpha Blending**: Professional transparency effects
- **Scale Variation**: Nested visual depth

### Professional Color Science
- **HSV Color Space**: Smooth hue transitions
- **Genre-based Palettes**: Musical style-appropriate colors
- **Real-time Adaptation**: Colors change with detected music
- **Smooth Interpolation**: No jarring color jumps

---

## 🔧 Troubleshooting

### Common Issues

#### Audio Not Detected
**Symptoms**: No visual response to music
**Solutions**:
1. Check BlackHole installation and configuration
2. Verify system audio routing
3. Test with different audio sources
4. Check Python audio permissions

#### Poor Performance
**Symptoms**: Low FPS, choppy visuals
**Solutions**:
1. Switch to Light Version for basic hardware
2. Lower resolution settings
3. Disable particle trails
4. Close other applications
5. Update graphics drivers

#### MIDI Controller Not Working
**Symptoms**: No response to MIDI input
**Solutions**:
1. Verify MIDI controller connection
2. Check MIDI port availability
3. Test with other MIDI software
4. Restart MIDI services

#### Python Import Errors
**Symptoms**: Module not found errors
**Solutions**:
```bash
# Reinstall dependencies
pip install --upgrade PySide6 numpy PyOpenGL librosa
```

### Performance Troubleshooting

#### Optimize for Your System
```python
# Light Version Settings (edit in code)
self.shape_resolution = 200          # Lower for better performance
self.target_fps = 30                 # Stable performance target
self.particle_trails = False         # Disable for speed
```

```python
# Standard Version Settings
self.musical_intelligence_frequency = 30  # Process less frequently
self.shape_resolution = 800              # Reduce if needed
self.layer_count = 2                     # Fewer layers = better performance
```

---

## ⚡ Performance Optimization

### Light Version Optimization
- **Already optimized** for basic hardware
- **No changes needed** for typical use
- **Consider**: Reducing window size if still choppy

### Standard Version Tuning
```python
# Edit these values in mmpa_standard.py for your system:

# For better performance:
self.target_fps = 30                    # Lower FPS target
self.musical_intelligence_frequency = 30 # Less frequent processing
self.shape_resolution = 600             # Lower resolution
self.layer_count = 2                    # Fewer layers

# For better quality (if performance allows):
self.target_fps = 60                    # Higher FPS
self.musical_intelligence_frequency = 10 # More frequent processing
self.shape_resolution = 1200            # Higher resolution
```

### Pro Version Configuration
The Pro Version is designed for maximum quality and performance on high-end systems. If experiencing issues:

1. **Monitor Performance**: Use built-in FPS counter
2. **Adjust Resolution**: Lower from 2000 to 1500 if needed
3. **Reduce Layers**: Set to 3-4 instead of 5-7
4. **Check Hardware**: Ensure adequate cooling and power

---

## 🎼 Professional Applications

### Live Performance Setup
#### Equipment Recommendations:
- **Computer**: High-end laptop or desktop
- **Audio**: Professional audio interface (RME, Focusrite)
- **MIDI**: MPK Mini or full 88-key controller
- **Display**: Large monitor or projector
- **Backup**: Secondary computer with Light Version

#### Performance Workflow:
1. **Pre-show**: Load Pro Version, test all connections
2. **Sound Check**: Verify audio routing and visual response
3. **Performance**: Use MIDI for real-time visual control
4. **Backup**: Have Light Version ready for quick fallback

### Studio Integration
#### Recording Setup:
```python
# Use recording functionality (Standard/Pro versions)
1. Start recording before performance
2. Capture visual morphing data
3. Export timeline for later playback
4. Integrate with DAW workflow
```

### Educational Applications
#### Classroom Use:
- **Music Theory**: Visualize key signatures and chord progressions
- **Audio Engineering**: Demonstrate frequency analysis
- **Computer Graphics**: Explore 3D geometry and morphing
- **Mathematics**: Klein bottles, Möbius strips, golden ratio

### Art Installations
#### Installation Setup:
- **Pro Version**: Maximum visual impact
- **Continuous Operation**: Test for 24/7 stability
- **Multiple Displays**: Consider multi-screen setup
- **Remote Monitoring**: Network-based performance monitoring

---

## 🎯 Version Comparison Summary

| Feature | Light | Standard | Pro |
|---------|--------|----------|-----|
| **Performance Target** | 30 FPS | 45 FPS | 60+ FPS |
| **Shape Library** | 6 basic | 9 enhanced | 9 professional |
| **Musical Intelligence** | ❌ | ✅ Throttled | ✅ Maximum |
| **Multi-layer Morphing** | ❌ | ✅ 3 layers | ✅ 7 layers |
| **Audio Processing** | MIDI only | BlackHole | Professional |
| **Particle Effects** | ❌ | ✅ Basic | ✅ Advanced |
| **Preset Management** | ❌ | ✅ 6 presets | ✅ 5 pro presets |
| **Recording System** | ❌ | ✅ JSON export | ✅ Pro recording |
| **Timeline Automation** | ❌ | ✅ Basic | ✅ Advanced |
| **Memory Usage** | <100MB | 100-300MB | 300-500MB |
| **CPU Load** | <20% | 20-50% | 50-80% |

---

## 🚀 Getting Started Recommendations

### New Users
1. **Start with Standard Version** - Best balance of features and performance
2. **Test with simple music** - Start with solo piano or acoustic guitar
3. **Experiment with shapes** - Try different morphing combinations
4. **Learn keyboard shortcuts** - Improve workflow efficiency

### Professional Users
1. **Use Pro Version** - Maximum quality and features
2. **Professional audio setup** - Dedicated audio interface
3. **Performance monitoring** - Watch FPS and adjust settings
4. **Custom presets** - Create genre-specific configurations

### Developers
1. **Study the framework** - MMPA Signal Engine architecture
2. **Extend functionality** - Add new shapes or analysis
3. **Custom processors** - Create new signal processing modules
4. **Contribute back** - Share improvements with community

---

## 📞 Support and Community

### Getting Help
- **Documentation**: This guide covers most use cases
- **Code Comments**: Each file is thoroughly documented
- **Test Scripts**: Use included test files for debugging

### Reporting Issues
- **Performance Issues**: Include system specifications
- **Audio Problems**: Describe audio setup and routing
- **Visual Glitches**: Include graphics card information

### Advanced Customization
- **Shape Creation**: Add new geometric forms
- **Audio Analysis**: Extend musical intelligence
- **Visual Effects**: Custom rendering techniques
- **Hardware Integration**: New MIDI controller support

---

**🎵 Enjoy creating beautiful audio-visual experiences with MMPA! 🎵**

*The Musical/Media Processing Architecture (MMPA) system transforms any musical performance into a stunning visual experience. From simple MIDI morphing to professional-grade musical intelligence, MMPA adapts to your needs and hardware capabilities.*