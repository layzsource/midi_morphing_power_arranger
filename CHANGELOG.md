# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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