# 🎛️ MMPA MIDI CC MAPPING GUIDE

**Professional VJ Controller Setup for MMPA (MIDI Morphing Power Arranger)**

---

## 🎯 **Quick Setup - Essential Controls**

### **Portal Warp Drive (Primary Performance Controls)**
- **CC 1** → X-Axis Portal Warp (Orbital camera movement)
- **CC 4** → Y-Axis Portal Warp (Vertical camera movement)
- **CC 5** → Zoom/Scale Control (0.5x - 1.5x range)

### **Performance Controls**
- **CC 2** → Time Warp (Temporal playback speed: 0.1x - 3.0x)
- **CC 3** → Shadow Intensity (Shadow visibility: 0x - 2.0x)
- **CC 7** → Cartridge Index (Sprite cartridge selector: 0-9)

---

## 🎚️ **Complete MIDI CC Map**

| CC# | Control Name | Range | Curve | Description |
|-----|--------------|--------|--------|-------------|
| **1** | Portal Warp X | 0-127 | Exponential | Orbital camera rotation around scene |
| **2** | Time Warp | 0-127 | Logarithmic | Temporal playback speed (0.1x-3.0x) |
| **3** | Shadow Intensity | 0-127 | Linear | Shadow visibility multiplier (0x-2.0x) |
| **4** | Portal Warp Y | 0-127 | Exponential | Vertical camera movement (full ceiling/floor range) |
| **5** | Portal Zoom | 0-127 | Linear | Camera zoom/scale (10%-200%) |
| **6** | Shape Rotation | 0-127 | Exponential | 3-axis rotation velocity (±10 dead zone, turntable feel) |
| **7** | Cartridge Index | 0-127 | Linear | Sprite cartridge selector (0-9) |
| **8** | Rotation Axis Toggle | 0-127 | Linear | 0-42=X(pitch), 43-84=Y(yaw), 85-127=Z(spin) |
| **16** | Ring Mask 1 (Front) | 0-127 | Digital | >63 = On, <64 = Off |
| **17** | Ring Mask 2 (Back) | 0-127 | Digital | >63 = On, <64 = Off |
| **18** | Ring Mask 3 (Right) | 0-127 | Digital | >63 = On, <64 = Off |
| **19** | Ring Mask 4 (Left) | 0-127 | Digital | >63 = On, <64 = Off |
| **20** | Ring Mask 5 (Top) | 0-127 | Digital | >63 = On, <64 = Off |
| **21** | Ring Mask 6 (Bottom) | 0-127 | Digital | >63 = On, <64 = Off |
| **50** | Ring 0 Size | 0-127 | Linear | Front ring scale (10%-200%) |
| **51** | Ring 0 Opacity | 0-127 | Linear | Front ring transparency (0%-100%) |
| **52** | Ring 0 Rotation | 0-127 | Logarithmic | Front ring rotation speed (0x-2.0x) |
| **53** | Ring 0 Distortion | 0-127 | Linear | Front ring shape distortion (0%-100%) |
| **54** | Ring 1 Size | 0-127 | Linear | Back ring scale (10%-200%) |
| **55** | Ring 1 Opacity | 0-127 | Linear | Back ring transparency (0%-100%) |
| **56** | Ring 1 Rotation | 0-127 | Logarithmic | Back ring rotation speed (0x-2.0x) |
| **57** | Ring 1 Distortion | 0-127 | Linear | Back ring shape distortion (0%-100%) |
| **58** | Ring 2 Size | 0-127 | Linear | Right ring scale (10%-200%) |
| **59** | Ring 2 Opacity | 0-127 | Linear | Right ring transparency (0%-100%) |
| **60** | Ring 2 Rotation | 0-127 | Logarithmic | Right ring rotation speed (0x-2.0x) |
| **61** | Ring 2 Distortion | 0-127 | Linear | Right ring shape distortion (0%-100%) |
| **62** | Ring 3 Size | 0-127 | Linear | Left ring scale (10%-200%) |
| **63** | Ring 3 Opacity | 0-127 | Linear | Left ring transparency (0%-100%) |
| **64** | Ring 3 Rotation | 0-127 | Logarithmic | Left ring rotation speed (0x-2.0x) |
| **65** | Ring 3 Distortion | 0-127 | Linear | Left ring shape distortion (0%-100%) |
| **66** | Ring 4 Size | 0-127 | Linear | Top ring scale (10%-200%) |
| **67** | Ring 4 Opacity | 0-127 | Linear | Top ring transparency (0%-100%) |
| **68** | Ring 4 Rotation | 0-127 | Logarithmic | Top ring rotation speed (0x-2.0x) |
| **69** | Ring 4 Distortion | 0-127 | Linear | Top ring shape distortion (0%-100%) |
| **70** | Ring 5 Size | 0-127 | Linear | Bottom ring scale (10%-200%) |
| **71** | Ring 5 Opacity | 0-127 | Linear | Bottom ring transparency (0%-100%) |
| **72** | Ring 5 Rotation | 0-127 | Logarithmic | Bottom ring rotation speed (0x-2.0x) |
| **73** | Ring 5 Distortion | 0-127 | Linear | Bottom ring shape distortion (0%-100%) |
| **80** | Effect: Blur | 0-127 | Digital | Toggle blur effect |
| **81** | Effect: Invert | 0-127 | Digital | Toggle color inversion |
| **82** | Effect: Chromatic | 0-127 | Digital | Toggle chromatic aberration |
| **83** | Effect: Echo | 0-127 | Digital | Toggle echo/delay effect |
| **84** | Effect: Strobe | 0-127 | Digital | Toggle strobe effect |
| **85** | Effect: Kaleidoscope | 0-127 | Digital | Toggle kaleidoscope effect |
| **90** | Portal Preset 1 | 0-127 | Digital | Load portal preset 1 (>63 = trigger) |
| **91** | Portal Preset 2 | 0-127 | Digital | Load portal preset 2 (>63 = trigger) |
| **92** | Portal Preset 3 | 0-127 | Digital | Load portal preset 3 (>63 = trigger) |
| **93** | Portal Preset 4 | 0-127 | Digital | Load portal preset 4 (>63 = trigger) |
| **94** | Portal Preset 5 | 0-127 | Digital | Load portal preset 5 (>63 = trigger) |
| **95** | Portal Preset 6 | 0-127 | Digital | Load portal preset 6 (>63 = trigger) |

---

## 🎛️ **Hardware Controller Recommendations**

### **Professional Grade:**
1. **Akai APC40 MkII** - Perfect layout for MMPA controls
   - Knobs 1-8 → Portal controls + effects
   - Channel faders → Ring masks
   - Scene launch buttons → Cartridge selection

2. **Novation Launch Control XL** - Dedicated knob controller
   - Top row → Portal warp controls (CC 1, 4, 5)
   - Middle row → Performance controls (CC 2, 3, 7)
   - Bottom row → Effects (CC 80-85)

3. **Behringer BCF2000** - Full-featured mixing console
   - 8 rotary encoders for all primary controls
   - 8 motorized faders for real-time feedback
   - Extensive MIDI mapping capabilities

### **Budget Options:**
1. **Korg nanoKONTROL2** - Compact and affordable
   - 8 knobs for essential controls
   - 8 faders for ring masks
   - Transport buttons for cartridge selection

2. **Arturia BeatStep** - Step sequencer + controller
   - 16 encoders for comprehensive control
   - Pressure-sensitive pads for effects

---

## ⚙️ **Control Curves Explained**

### **Linear (1:1 Response)**
- **Best For:** Precise control, digital switches
- **Used On:** Shadow Intensity, Zoom, Ring Masks, Effects

### **Exponential (Accelerated Response)**
- **Best For:** Natural-feeling camera movement
- **Used On:** Portal Warp X & Y axes
- **Effect:** Slow at start, fast at end

### **Logarithmic (Smooth Scaling)**
- **Best For:** Time/speed controls
- **Used On:** Time Warp
- **Effect:** Fast at start, slow at end

---

## 🎭 **Performance Workflow Examples**

### **Cinematic Camera Work:**
1. **CC 1 (Portal X)** → Slow orbital sweeps around scene
2. **CC 4 (Portal Y)** → Dramatic high/low angle shots
3. **CC 5 (Zoom)** → Push in for intensity, pull out for overview
4. **Smoothing ON** → Cinematic motion blur effects

### **Precise VJ Control:**
1. **Smoothing OFF** → Instant response to beats
2. **CC 1 + 4** → Quick position changes on musical hits
3. **CC 80-85** → Rapid effect toggles for drops/builds
4. **CC 7** → Switch cartridges for different visual themes

### **Live Audio Sync:**
1. **CC 2 (Time Warp)** → Match visual speed to BPM changes
2. **CC 3 (Shadow Intensity)** → Fade shadows during quiet sections
3. **Portal controls** → Follow musical dynamics
4. **Beat Sync ON** → Automatic strobe sync to detected beats

### **Preset-Based Performance:**
1. **CC 90-95** → Instant portal position changes via MIDI triggers
2. **Right-click presets** → Save custom positions during practice
3. **Preset chains** → Program controller to sequence through presets
4. **Live morphing** → Use manual controls between preset jumps

### **Ring Morphing Techniques:**
1. **CC 50-73** → Individual ring transformation control
2. **Size morphing** → Create breathing/pulsing ring effects
3. **Opacity fades** → Layer rings in and out during musical sections
4. **Rotation sync** → Match ring spins to BPM for hypnotic effects
5. **Distortion waves** → Shape rings dynamically for organic movement

---

## 🔧 **Technical Setup Notes**

### **MIDI Channel:** Channel 1 (default)
### **Latency:** <50ms guaranteed for professional performance
### **Velocity Sensitivity:** Not used (CC values only)
### **Program Changes:** Not implemented (use CC 7 for cartridge switching)

### **Browser Compatibility:**
- ✅ **Chrome/Edge:** Full Web MIDI API support
- ✅ **Firefox:** Requires manual MIDI permission
- ❌ **Safari:** Limited Web MIDI support (use Chrome)

### **Hardware Setup:**
1. Connect MIDI controller via USB
2. Launch MMPA in Chrome/Edge
3. Grant MIDI permissions when prompted
4. Controller mappings activate automatically
5. Test with Portal Warp controls (CC 1, 4, 5)

---

## 🎪 **Advanced Mapping Ideas**

### **Multi-Controller Setup:**
- **Controller A:** Portal warp drive (CC 1, 4, 5)
- **Controller B:** Effects and ring masks (CC 16-21, 80-85)
- **Controller C:** Cartridge management (CC 7) + performance controls

### **Custom Control Surfaces:**
```javascript
// Example: Map foot pedal to zoom for hands-free operation
midiInput.addEventListener('midimessage', (event) => {
    if (event.data[0] === 176 && event.data[1] === 64) { // CC 64 (sustain pedal)
        portalZoom = event.data[2] / 127; // Convert to 0-1 range
    }
});
```

### **OSC Integration (Future):**
- TouchOSC layouts for mobile control
- Max/MSP integration for advanced automation
- Ableton Live integration via Max4Live

---

## 🚨 **Troubleshooting**

### **No MIDI Response:**
1. Check Web MIDI API support (chrome://flags/#enable-web-midi)
2. Verify MIDI device connection
3. Grant browser MIDI permissions
4. Restart browser if needed

### **Laggy/Delayed Response:**
1. Close other browser tabs
2. Check system audio latency settings
3. Use dedicated MIDI interface (not USB-to-MIDI adapter)
4. Enable "Precise Mode" for instant response

### **Effects Not Working:**
1. Verify CC 80-85 mapping
2. Check effect toggle state in UI
3. Effects require >63 value to activate
4. Some effects only visible with specific content

---

## 📊 **Performance Optimization**

### **For Live Performance:**
- Enable **Smoothing OFF** for tight sync
- Use **CC 1, 4, 5** as primary performance controls
- Pre-load cartridges with complementary visual content
- Test all mappings before going live

### **For Installation/Ambient:**
- Enable **Smoothing ON** for fluid motion
- Use **CC 2 (Time Warp)** for slow-motion effects
- Map **CC 3 (Shadow Intensity)** to audio analysis
- Automate portal movement with long-period LFOs

---

**Ready to rock the visual universe! 🌟**

*For technical support or advanced mapping requests, consult the main MMPA documentation or join the community forums.*