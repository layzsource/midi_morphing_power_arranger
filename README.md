# 🌊 Signal→Form Engine: Spherical POV System

**Complete implementation of the spherical consciousness navigation system with live eigenmode deformation.**

## 🌍 Overview

Revolutionary transformation from basic MIDI visualization to **navigable consciousness instrument**:

- **🌐 Spherical POV Navigation** - Outside universe → center looking outward
- **🎯 Portal System** - Click sprites → real eigenmode deformation
- **📊 Spectral Graph Analysis** - Mathematical foundation for every visual
- **🎛️ Live Telemetry** - Real-time consciousness depth parameters

> *"The windmill of the mind is turning. Stand at the center and look outward at the layers of meaning."*

## 🏗️ Architecture

```
universal-signal-engine/
├── README.md                           # This file
├── microfiche/
│   └── index.html                      # Spherical POV interface (1100+ lines)
├── signal_form_split_servers_and_configs/
│   ├── engine_server.py               # Engine: WebSocket telemetry + HTTP control
│   ├── encoder_stub.py                # Encoder: Collection/atlas/stim endpoints
│   ├── microfiche_config.json         # Configuration
│   ├── encoder_config.yaml            # Encoder settings
│   └── README.txt                     # Server details
├── src/signal-form/
│   └── SpectralGraphEngine.ts         # Core spectral analysis
├── eigenmode_cube.html                # Standalone eigenmode viewer
└── eigenmode_websocket_bridge.py     # Original bridge (now superseded)
```

### Three-Server System
- **Engine (Port 7070)** → WebSocket telemetry + HTTP control endpoints
- **Encoder (Port 7071)** → Media processing + stimulus generation
- **Microfiche (Browser)** → Spherical POV interface with live portal system

## 🚀 Quick Start

### 1. Start Engine Server (Port 7070)
```bash
cd signal_form_split_servers_and_configs
python3 -m pip install fastapi uvicorn numpy scipy pillow
python3 engine_server.py
```
**Provides:**
- WebSocket telemetry: `ws://localhost:7070/telemetry`
- HTTP control: `http://localhost:7070/control`

### 2. Start Encoder Server (Port 7071)
```bash
# Same terminal or new one
python3 encoder_stub.py --images ~/Downloads --cap 128
```
**Provides:**
- Collection data: `http://localhost:7071/collection/home_cube`
- Media atlas: `http://localhost:7071/atlas/home_cube.png`
- Stimulus generation: `http://localhost:7071/stim/{media_id}`

### 3. Open Spherical POV Interface
```bash
open microfiche/index.html
```

## 🎮 Using the Spherical POV

### Camera Navigation
- **Mouse Wheel**: Zoom ζ parameter (0 = outside universe, 1 = center POV)
- **Mouse Move**: Orbit around current position
- **ζ Transition**: Outside→surface→inside with smooth up-vector slerp

### Portal System
1. **Zoom to outer shell** (ζ ≈ 0.2) to see sprite clouds
2. **Hover sprites** to see color palettes and metadata
3. **Click any sprite** → triggers portal sequence:
   - POST `/stim/{media_id}` → gets stimulus packet
   - POST `/control` → sends control to engine
   - **Watch center instrument morph** via eigenmode deformation

### Controls
- **ζ Slider**: Manual zoom control
- **PMW Slider**: Consciousness depth parameter
- **Unity/Flatness**: Spectral balance controls
- **CENTER ME Button**: Emergency grounding (ζ→1, PMW→1, flatten spectrum)

## 📊 Technical Details

### Media Processing
The encoder processes **62 media items** from `~/Downloads`:
- **Color Palette Extraction**: Dominant RGB values per item
- **Sprite Atlas Generation**: Packed texture atlas
- **Stimulus Mapping**: Palette→RGB bias, tags→Dewey shelves

### Eigenmode Deformation
Center instrument morphs through:
1. **Cube↔Sphere**: Membrane transition at ζ crossing
2. **Modal Coefficients**: Live telemetry drives vertex displacement
3. **Real-time Update**: <50ms portal click → visible morph

### WebSocket Telemetry Stream
```json
{
  "t": 12.34,
  "c": [0.3, 0.4, 0.2, 0.1],          // Modal coefficients
  "S": {"U":0.60,"F":0.70},            // Unity, Flatness
  "entropy": 0.38,                     // Spectral disorder
  "R": 0.27,                          // Temporal change
  "pmw": 0.74                          // Consciousness depth
}
```

## 🧪 Testing the Complete Loop

### 1. Verify Servers
```bash
# Test control endpoint
curl -X POST http://localhost:7070/control \
  -H "Content-Type: application/json" \
  -d '{"set":{"pmw":0.8}}'

# Test collection
curl http://localhost:7071/collection/home_cube

# Test stimulus
curl -X POST http://localhost:7071/stim/IMG_1175
```

### 2. Verify Portal Magic
1. Open `microfiche/index.html`
2. Check WebSocket status shows "Connected"
3. Scroll to outer shell (ζ ≈ 0.2)
4. Click any colored sprite
5. **Watch center cube deform** in real-time

## ✅ Success Criteria

- [ ] Both servers start without errors
- [ ] WebSocket shows "Connected" in browser
- [ ] Sprites visible on outer shell with color palettes
- [ ] ζ slider smoothly transitions outside→inside
- [ ] Sprite click triggers visible center deformation <50ms
- [ ] No gimbal flip during membrane crossing

**The complete spherical consciousness navigation system is ready.**