# fig Project Roadmap

## 🏗️ Unified Project Architecture
```
fig/
│
├── main.py                  # Entry point (launch EnhancedApplication)
├── core/
│   ├── app.py               # Orchestration (like EnhancedApplication)
│   ├── config.py            # Settings (audio backend, presets, quality, etc.)
│   └── utils.py             # Shared helpers (math, color mapping, etc.)
│
├── audio/
│   ├── audio_handler.py     # Backend switching (SoundDevice, PyAudio)
│   ├── audio_analysis.py    # Full spectral features (centroid, flux, MFCC, etc.)
│   ├── onset_detection.py   # Adaptive onset + tempo tracking
│   └── feature_signals.py   # Qt signals for bass/mid/treble, beats, flux, etc.
│
├── midi/
│   ├── midi_handler.py      # Note/CC input, device management
│   ├── midi_mapping.py      # Map MIDI events → visual/lighting actions
│   └── presets.py           # Instrument presets (piano, drums, synth, orchestral)
│
├── visuals/
│   ├── scene_manager.py     # Manage objects, camera, lighting, presets
│   ├── particles.py         # Full particle system with physics
│   ├── morphing_shapes.py   # Shape objects + morphing engine
│   ├── geometry_library.py  # Sphere, cube, torus, helix, Möbius, fractals, terrain
│   ├── mesh_ops.py          # Morphing, twist, noise, wave deformations
│   └── lighting.py          # Stage lighting system (point, spot, ambient, MIDI-reactive)
│
├── monitoring/
│   ├── performance.py       # FPS, memory, CPU, auto-quality scaling
│   └── recorder.py          # Record/playback performances
│
└── gui/
    ├── main_window.py       # PySide6/PyQt6 GUI (menu, controls, visualization viewport)
    └── widgets/             # Custom widgets (circle of 5ths, spectrum visualizer, etc.)
```

---

## 🎵 Audio System
- **`audio_handler.py`**
  - Abstraction layer for multiple backends (SoundDevice, PyAudio).
  - Threaded input stream, emits audio buffers.

- **`audio_analysis.py`**
  - Spectral centroid, rolloff, bandwidth.
  - Zero-crossing rate.
  - MFCC, mel spectrogram.
  - Spectral flux.
  - Beat detection and tempo tracking.

- **`onset_detection.py`**
  - Adaptive threshold onset detection.
  - Emits beat/onset signals.

- **`feature_signals.py`**
  - Central hub for Qt signals:
    - `bass_energy`, `mid_energy`, `treble_energy`
    - `onset_detected`
    - `tempo_changed`
    - `spectral_flux`

---

## 🎮 MIDI System
- **`midi_handler.py`**
  - Device discovery + hot-plugging.
  - Note on/off, CC changes, channel filtering.

- **`midi_mapping.py`**
  - Map MIDI note/CC → particle burst, morph preset, lighting scene.
  - Configurable mapping system (JSON/yaml file).

- **`presets.py`**
  - Preset mappings for common instruments:
    - Piano → circle of 5ths, harmonic colors.
    - Drums → bursts + strobe lights.
    - Synth → wave morphs + ambient lighting.
    - Orchestral → layered morphs + directional lights.

---

## 🎨 Visuals
- **`scene_manager.py`**
  - Handles multiple visual objects (shapes, lights, particle systems).
  - Preset scenes (circle, spiral, dome, random).

- **`particles.py`**
  - Full particle system with gravity, drag, turbulence, bursts.
  - Audio and MIDI reactive emission.

- **`morphing_shapes.py`**
  - Objects that morph between meshes.
  - Animation modes: pulse, rotate, breathe, strobe, wave.

- **`geometry_library.py`**
  - Shapes: sphere, cube, torus, cone, pyramid, cylinder, helix, Möbius strip, Klein bottle, fractal meshes, terrain.

- **`mesh_ops.py`**
  - Morphing between arbitrary meshes (automatic resampling).
  - Deformations: twist, wave, noise.
  - Mesh info extraction: bounds, volume, area.

- **`lighting.py`**
  - Lighting modes: ambient, point, spot, directional.
  - MIDI note → lighting color/intensity.
  - Concert presets: strobes, moving lights, rainbow cycles.

---

## 📊 Monitoring
- **`performance.py`**
  - FPS/memory/CPU monitoring.
  - Adaptive quality scaling (like `v2_clean`).

- **`recorder.py`**
  - Record live performance (audio/MIDI/visuals).
  - Playback mode for testing/rehearsal.

---

## 🖥️ GUI
- **`main_window.py`**
  - PySide6 window with:
    - Visualization viewport (OpenGL/Qt3D/Unreal bridge).
    - Control panel (choose presets, lighting modes, MIDI mappings).
    - Live indicators (spectrogram, circle of 5ths, FFT bands).

- **`widgets/`**
  - Circle of 5ths widget (interact with scales/modes).
  - MIDI activity monitor (keys lighting up).
  - Performance graphs (FPS, CPU).

---

## 🏆 End Result
By merging:
- **`main.py`** → advanced spectral analysis & onset detection.
- **`v2_clean`** → stable visuals, particles, MIDI.
- **`refactored`** → clean modular architecture.

You’ll have a **professional-grade, modular, extensible AV engine** — suitable for live shows, education, or integration into Unreal for commercial deployment.
