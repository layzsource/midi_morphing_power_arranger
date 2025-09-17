# 🎼 fig Master Plan

This document combines the **Roadmap**, **Migration Checklist**, and **Migration Timeline**.

---

## 🗺️ Roadmap

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


---

## ✅ Migration Checklist

# ✅ fig Migration Checklist

## 1. Core Setup
- [ ] Create `fig/` folder with submodules (`core`, `audio`, `midi`, `visuals`, `monitoring`, `gui`).
- [ ] Move `new_fixed_refactored.py` → `core/app.py` (rename class to `EnhancedApplication`).
- [ ] Add `core/config.py` for backend settings, presets, defaults.
- [ ] Add `core/utils.py` (math helpers, color mapping, signal smoothing).

---

## 2. Audio System
- [ ] Port **basic audio handler** (`AudioHandler` from refactored).
- [ ] Add **backend switching** (`sounddevice`, `PyAudio`) in `audio_handler.py`.
- [ ] Migrate advanced **spectral analysis** from `main.py` → `audio_analysis.py`.
  - [ ] Spectral centroid, rolloff, bandwidth.
  - [ ] Zero-crossing rate.
  - [ ] MFCC + mel spectrogram (via `librosa`).
  - [ ] Spectral flux.
- [ ] Implement **onset detection + tempo tracking** in `onset_detection.py`.
- [ ] Create **Qt signal hub** (`feature_signals.py`) for all extracted features.

---

## 3. MIDI System
- [ ] Create `midi_handler.py` with **device discovery + hot-plugging**.
- [ ] Port **MIDI input handling** from `v2_clean.py`.
- [ ] Add **midi_mapping.py** (map Note/CC → particles, morphs, lighting).
- [ ] Build **presets.py** (piano, drums, synth, orchestral mappings).

---

## 4. Visuals
- [ ] Port **particle system** from `v2_clean.py` → `particles.py`.
  - [ ] Physics: gravity, drag, turbulence.
  - [ ] Particle bursts triggered by MIDI + audio peaks.
- [ ] Move **morphing shapes** (from `v2_clean.py`) → `morphing_shapes.py`.
- [ ] Expand `geometry_library.py` with shapes:
  - Sphere, cube, torus, cylinder, cone, pyramid.
  - Helix, Möbius strip, Klein bottle, fractals, terrain.
- [ ] Implement **mesh_ops.py** for morphing + deformations (twist, wave, noise).
- [ ] Add **lighting.py** system:
  - Ambient, point, spot, directional lights.
  - MIDI-responsive lighting (note intensity → brightness/color).
  - Stage presets (strobe, rainbow cycle, concert lighting).
- [ ] Create **scene_manager.py** to handle presets (circle, spiral, dome, grid).

---

## 5. Monitoring
- [ ] Port **performance monitoring** from `v2_clean.py` → `performance.py`.
- [ ] Add **recorder.py** for performance recording & playback.

---

## 6. GUI
- [ ] Create `main_window.py` (PySide6/PyQt6).
  - [ ] Integrate visualization viewport (OpenGL/Qt3D/Unreal).
  - [ ] Add side panel for presets, lighting, MIDI mapping.
  - [ ] Add performance indicators.
- [ ] Build `widgets/`:
  - Circle of 5ths + scale/mode selector.
  - Live spectrogram viewer.
  - MIDI activity monitor.

---

## 7. Integration
- [ ] Update `core/app.py` to connect:
  - Audio features → visual + MIDI responses.
  - MIDI events → particles, morphs, lighting.
- [ ] Test threading + Qt signals for safety.
- [ ] Test presets (e.g., piano mode, synth mode).
- [ ] Add config options for **backend selection** (SoundDevice vs PyAudio).

---

## 8. Stretch Goals
- [ ] Unreal Engine bridge (Qt3D → Unreal).
- [ ] Export **recorded performances** to video.
- [ ] VR/AR mode (OpenXR or Unreal integration).
- [ ] Add **procedural generation** (terrain, fractals evolving over time).

---

👉 This checklist gives you a **migration roadmap + dev to-do list**.
You could even paste it into your GitHub repo as `MIGRATION_CHECKLIST.md` and tick off items as you implement them.


---

## 📅 Migration Timeline

# 📅 fig Migration Timeline (Suggested Sprints)

## 🕐 Week 1: Foundation
- ✅ Create `fig/` folder + module structure.
- ✅ Move `new_fixed_refactored.py` → `core/app.py`.
- ✅ Add `config.py` (set audio backend defaults, presets).
- ✅ Add `utils.py` (color mapping, math helpers).
- 🔲 Build first working loop: open `main_window.py`, start `AudioHandler`, see GUI update.

---

## 🕑 Week 2: Audio Core
- 🔲 Port **AudioHandler** (sounddevice + PyAudio backend switch).
- 🔲 Implement **basic spectral analysis** (centroid, rolloff, bandwidth).
- 🔲 Add **feature_signals.py** (Qt signals for features).
- 🔲 Connect GUI to display FFT bands or energy bars.

---

## 🕒 Week 3: Advanced Audio
- 🔲 Add **librosa features** (MFCC, mel spectrogram, spectral flux).
- 🔲 Add **onset detection** + **tempo tracking**.
- 🔲 Emit signals for beat/onset → test with simple “pulse” visuals.
- 🔲 Verify threading + signal safety.

---

## 🕓 Week 4: MIDI System
- 🔲 Create `midi_handler.py` with hot-plugging.
- 🔲 Port MIDI input from `v2_clean.py`.
- 🔲 Add `midi_mapping.py` (map notes → visuals).
- 🔲 Build `presets.py` (piano, drums, synth).
- 🔲 Test: play MIDI keyboard, trigger particle bursts.

---

## 🕔 Week 5: Visual Core
- 🔲 Port **particle system** from `v2_clean.py`.
- 🔲 Port **morphing shapes** (sphere → cube morph).
- 🔲 Add `scene_manager.py` to hold multiple shapes/particles.
- 🔲 Implement simple **lighting** (ambient + pulse).

---

## 🕕 Week 6: Geometry + Mesh Ops
- 🔲 Expand `geometry_library.py` with advanced shapes (torus, Möbius, fractal).
- 🔲 Add `mesh_ops.py` for morphing & deformations.
- 🔲 Connect audio + MIDI to control mesh morphing.
- 🔲 Build first **scene presets** (circle layout, spiral, dome).

---

## 🕖 Week 7: Monitoring + Recording
- 🔲 Port performance monitor from `v2_clean.py`.
- 🔲 Add **adaptive quality scaling** (auto adjust particle count).
- 🔲 Implement `recorder.py` (record/playback performances).
- 🔲 Add FPS/memory indicators to GUI.

---

## 🕗 Week 8: GUI Expansion
- 🔲 Build control panel in `main_window.py`.
- 🔲 Add widgets:
  - Circle of 5ths scale selector.
  - MIDI activity monitor.
  - Spectrogram visualizer.
- 🔲 Add scene/lighting preset dropdowns.

---

## 🕘 Stretch Goals (Weeks 9+)
- 🔲 Unreal bridge (Qt → Unreal for rendering).
- 🔲 Export recordings as video.
- 🔲 VR/AR integration (OpenXR or Unreal).
- 🔲 Procedural terrain + fractal generation.

---

👉 This plan assumes **1–2 weeks per major subsystem**, but you could go faster if you focus just on core features (audio + MIDI + visuals) before extras (recording, GUI polish).
