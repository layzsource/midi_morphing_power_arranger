# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-01-XX — 3D Audio Spatialization Engine

### Immersive Spatial Audio System
- **3D Audio Engine**: Integrated Web Audio API AudioContext with PannerNode + AudioListener for true 3D positional audio rendering
- **Binaural Processing**: HRTF-based binaural rendering with ConvolverNode for immersive headphone experience
- **Eigenmode Audio Mapping**: Dynamic mapping of eigenmode coefficients to 3D spatial positions and audio parameters
- **Sprite Audio Sources**: Each portal sprite rendered as individual positional audio source with distance attenuation

### Advanced Spatial Controls & Parameter Mapping
- **HUD Controls**: Added "3D Audio" toggle, "Spatial Mode" dropdown (binaural/stereo/ambient), "Spread" slider, and X/Y/Z Position controls
- **Eigenmode Mapping**: Automatic mapping of first 3 eigenmode coefficients to listener X/Y/Z position in 3D space
- **Parameter Integration**: Zeta (zoom) controls listener position, Unity/Flatness mapped to spatial spread and diffusion
- **Manual Positioning**: Direct control of listener position via HUD sliders with real-time collaborative sync
- **Ambient Soundscape**: Layered ambient audio with positional sprite playback for comprehensive spatial experience
- **Real-time Updates**: Continuous spatial audio updates synchronized with main animation loop

### Collaborative Spatial Audio Events
- **spectral_audio_enabled**: Real-time 3D audio toggle synchronization across all collaborative sessions
- **spectral_audio_mode**: Spatial mode switching (binaural/stereo/ambient) with user attribution and toast notifications
- **spectral_audio_spread**: Spatial spread parameter changes broadcast with enhanced user color feedback
- **spectral_audio_position**: Real-time listener position updates with x,y,z coordinates synchronized across sessions
- **Enhanced Toast System**: Contextual 3D audio notifications with user color coding and parameter-specific messages

### Backward Compatibility & Fallbacks
- **AudioContext Fallback**: Graceful fallback to flat stereo if AudioContext unavailable with UI state updates
- **Error Handling**: Comprehensive error handling with fallback states and disabled controls on initialization failure
- **Legacy Preservation**: All existing audio features and spectral analysis preserved unchanged
- **Progressive Enhancement**: 3D audio features layer on top of existing system without breaking changes

*"The 3D Audio Spatialization Engine transforms the Signal→Form Engine into an immersive spatial audio platform, mapping mathematical elegance to three-dimensional sonic space."*

---

## [0.3.0] - 2024-12-26 — Advanced Spectral Analysis

### Modal Energy Distribution & Temporal History
- **Modal Energy Visualization**: Color-coded frequency bands with dominant mode tracking, enhanced with exponential fade curves and pulsing energy indicators
- **Extended Waterfall Buffer**: Temporal band history buffer with 15-second persistence and scrolling spectrogram with enhanced color mapping
- **Frequency Grid Overlays**: Time and frequency grid lines for professional spectral analysis readability
- **Enhanced Color Palette**: Sub-bass through brilliance frequency range mapping with dynamic alpha blending

### Collaborative Spectral Events with Full User Attribution
- **spectral_enabled**: Real-time toggle synchronization across all collaborative sessions with toast notifications
- **spectral_mode**: Mode switching (bars, waterfall, modal_energy, temporal_evolution) with user attribution
- **spectral_fft_size**: FFT size changes broadcast with enhanced user color feedback
- **spectral_log_scale**: Linear/logarithmic frequency scaling toggle with collaborative sync
- **Enhanced Toast System**: Contextual spectral notifications with user color coding and 3-second auto-dismiss

### Performance & Compatibility
- **Efficient Rendering**: Optimized canvas operations with timestamp-based temporal fade calculations
- **Backward Compatibility**: All existing bars and waterfall modes preserved unchanged with no performance regressions
- **Collaborative Integration**: Seamless real-time parameter synchronization across multi-user sessions

*"Advanced spectral analysis modes transform the Signal→Form Engine into a professional-grade collaborative audio visualization platform."*

---

## [0.2.1] - 2024-12-26 — Spectral Overlay Refinements

### Enhanced FFT Controls & Visual Experience
- **Resizable and Draggable Interface**: FFT overlay can now be moved and resized anywhere on screen with proper boundary constraints
- **Quick FFT Size Presets**: One-click buttons for 256, 512, 1024, 2048 with active state highlighting
- **Enhanced Waterfall Visuals**: Smooth blue→cyan→yellow→orange→red gradient progression with ImageData rendering
- **Log-Frequency Scaling**: Toggleable LOG button for logarithmic vs linear frequency display
- **Performance Optimizations**: Cached gradients, ResizeObserver integration, and efficient canvas management

### Collaborative Toast Notifications
- **User Attribution**: Real-time notifications showing "UserX changed FFT size: 1024" with color-coded borders
- **Parameter-Specific Messages**: Contextual notifications for overlay toggle, visualization mode, FFT size, and log scaling changes
- **Non-Intrusive Design**: Top-right positioning with smooth slide-in animation and 3-second auto-dismiss

### Compatibility
- **Backward Compatible**: All existing HUD and collaborative flows preserved unchanged
- **Offline Graceful**: Enhanced FFT features cleanly disabled when collaboration unavailable

*"The FFT overlay is now a professional-grade spectral analysis tool, seamlessly integrated with the collaborative Signal→Form Engine."*

---

## [0.2.0] - 2024-12-25 — Collaborative Runtime

### New Multi-User Features
- **User Attribution**: Auto-generated usernames with consistent MD5-based colors for each participant
- **Portal Notifications**: Real-time notifications showing which user opened which portal (e.g., "UserX opened portal IMG_1234")
- **Slider Synchronization**: Parameter updates sync across all sessions with last-writer-wins conflict resolution and visual user color feedback
- **Chat Overlay**: Lightweight real-time messaging with timestamps and user attribution via floating 💬 button
- **Preset Sharing**: Users can share and apply presets across the entire collaborative session in real-time
- **JSON Payloads**: Well-structured event system with `collaborative_sprite_interaction`, `collaborative_parameter_update`, `collaborative_chat_message`, and `collaborative_preset_applied` message types

### Compatibility
- **Backward Compatibility**: All existing single-user flows preserved unchanged
- **Offline Mode**: Collaborative features cleanly disabled when no session parameters provided

This marks the collaborative milestone of the Signal→Form Engine, enabling true multi-user exploration.

---

## [0.1.0] - 2024-12-20

### Added
- Initial Signal→Form Engine implementation
- Multi-window state synchronization
- MIDI control integration
- Portal system for media interaction
- Basic parameter control system

### Infrastructure
- FastAPI-based engine server
- WebSocket telemetry system
- HTTP control endpoints
- Three.js visualization layer

---

*Generated with [Claude Code](https://claude.ai/code)*