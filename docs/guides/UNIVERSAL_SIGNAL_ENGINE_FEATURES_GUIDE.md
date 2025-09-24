# Universal Signal Engine Features Guide

## 🔍 **Ring Mask Matrix** - Individual Ring Control System

### What It Does
The **Ring Mask Matrix** controls the visibility of each of the 6 vessel rings individually, allowing you to:
- **Hide/Show Specific Rings**: Toggle visibility of Front, Back, Left, Right, Top, and Bottom rings
- **Create Compositions**: Build unique visual arrangements by masking certain rings
- **Shadow Theater Control**: Control which rings cast shadows during performance
- **Live Performance**: Real-time ring visibility manipulation for VJ sets

### Current Implementation
- **Location**: Acid Reign VJ Interface → Ring Mask Matrix section
- **6 Toggle Buttons**: FRONT, BACK, RIGHT, LEFT, TOP, BTM
- **Visual Feedback**: Active rings show cyan, inactive rings show dim
- **MIDI Control**: CC 16-21 (one CC per ring)

### Potential Uses Beyond VJ
1. **Debugging**: Isolate specific rings to test shadows or effects
2. **Educational**: Show how different ring positions affect the overall structure
3. **Art Creation**: Create minimalist compositions with selective ring display
4. **Performance Art**: Choreographed ring reveals/hides synced to music

---

## 🎚️ **Acid Effects Rack** - Real-Time Visual Effects System

### What Each Effect Does

#### 1. **BLUR** Effect
- **Function**: Applies motion blur or Gaussian blur to visuals
- **Performance Use**: Soften harsh edges, create dreamy transitions
- **Technical**: Post-processing shader effect on rendered output

#### 2. **INVERT** Effect
- **Function**: Inverts colors (black becomes white, colors flip)
- **Performance Use**: Dramatic contrast shifts, negative film effects
- **Technical**: Color inversion shader applied to final render

#### 3. **CHROME** (Chromatic Aberration)
- **Function**: Splits RGB channels creating color fringing
- **Performance Use**: Glitch aesthetics, retro CRT monitor effects
- **Technical**: RGB channel offset in different directions

#### 4. **ECHO** Effect
- **Function**: Temporal echo/delay of visual elements
- **Performance Use**: Trail effects, persistence of vision illusions
- **Technical**: Frame buffer blending with previous frames

#### 5. **STROBE** Effect
- **Function**: Rapid on/off flashing synchronized to beats
- **Performance Use**: Club/rave atmospherics, seizure warnings apply!
- **Technical**: Brightness modulation at audio-detected BPM

#### 6. **KALEIDO** (Kaleidoscope)
- **Function**: Mirror/reflect visuals in kaleidoscope patterns
- **Performance Use**: Psychedelic symmetrical patterns
- **Technical**: Fragment shader with radial mirroring

### Alternative Uses for Effects Rack
1. **Audio Visualization**: Map each effect to frequency bands
2. **MIDI Instrument**: Use effects as musical parameters
3. **Data Visualization**: Effects intensity represents data values
4. **Meditation Tool**: Gentle, slow-cycling effects for relaxation

---

## ⌨️ **Current Keyboard Controls**

### Vessel Rotation (Available Now)
- **Arrow Keys**:
  - `←` **Left Arrow**: Rotate vessel left (Y-axis)
  - `→` **Right Arrow**: Rotate vessel right (Y-axis)
  - `↑` **Up Arrow**: Rotate vessel up (X-axis)
  - `↓` **Down Arrow**: Rotate vessel down (X-axis)

### Microfiche Controls
- **Shift + Arrow**: Shadow viewing angle control
- **0-5 Keys**: Select specific ring index
- **` or ~**: Select all rings

---

## 📱 **Mobile-Friendly Control Proposal**

### Why Sliders Are Better for Mobile
1. **Touch-Friendly**: Large touch targets, easy to grab and drag
2. **Precise Control**: Smooth continuous values vs discrete button presses
3. **Visual Feedback**: Current value clearly displayed
4. **iPad Optimized**: Works perfectly with Apple Pencil
5. **Responsive Design**: Adapts to different screen sizes

### Proposed Mobile Control Panel

```
📱 UNIVERSAL SIGNAL ENGINE - MOBILE CONTROLS

┌─────────────────────────────────────────┐
│  🎛️ VESSEL ROTATION CONTROL             │
├─────────────────────────────────────────┤
│  X-Axis: [====●====] -180° ← → +180°   │
│  Y-Axis: [==●======] -180° ← → +180°   │
│  Z-Axis: [======●==] -180° ← → +180°   │
│                                         │
│  🔄 Motion: [ON ] [OFF]                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🟫 RING MASK MATRIX                    │
├─────────────────────────────────────────┤
│  [FRONT] [BACK ] [RIGHT]                │
│  [LEFT ] [TOP  ] [BTM  ]                │
│                                         │
│  Quick: [ALL ON] [ALL OFF] [RESET]      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🎚️ EFFECTS INTENSITY                   │
├─────────────────────────────────────────┤
│  Blur:    [===●===] 50%                 │
│  Invert:  [●======] 10%                 │
│  Chrome:  [======●] 90%                 │
│  Echo:    [==●====] 30%                 │
│  Strobe:  [●======] 0%                  │
│  Kaleido: [====●==] 60%                 │
│                                         │
│  Master:  [======●] 85%                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  🎵 AUDIO REACTIVE                      │
├─────────────────────────────────────────┤
│  Bass:    [======●] High                │
│  Mid:     [===●===] Medium              │
│  Treble:  [==●====] Low                 │
│                                         │
│  Key: E♭ Major  BPM: 128  📶 ●●●○○     │
└─────────────────────────────────────────┘
```

---

## 🛠️ **Implementation for Mobile Controls**

### 1. Responsive Slider Component
```typescript
interface MobileSlider {
    label: string;
    min: number;
    max: number;
    value: number;
    step?: number;
    unit?: string;
    onChange: (value: number) => void;
}
```

### 2. Touch-Optimized Layout
- **Large Touch Targets**: Minimum 44px tap targets
- **Swipe Gestures**: Horizontal swipe for rotation, vertical for intensity
- **Haptic Feedback**: Vibration on value changes (mobile browsers)
- **Visual Feedback**: Real-time preview of changes

### 3. Advanced Mobile Features
- **Gyroscope Control**: Use phone orientation for vessel rotation
- **Multi-Touch**: Two-finger pinch for zoom, three-finger tap for effects
- **Gesture Recognition**: Custom gestures for frequently used functions
- **Voice Control**: "Rotate left", "Toggle front ring", "Increase bass"

---

## 🎯 **Recommended Control Mapping for Different Use Cases**

### 1. **VJ Performance** (Current Implementation)
- MIDI controller for precise real-time control
- Keyboard shortcuts for quick access
- Large display with visual feedback

### 2. **Mobile/Tablet Creative** (Proposed)
- Touch sliders for smooth parameter control
- Large buttons for effects on/off
- Gesture support for intuitive interaction

### 3. **Web Demo/Education** (Hybrid Approach)
- Click-and-drag sliders that work with mouse
- Keyboard shortcuts for advanced users
- Help tooltips explaining each feature

### 4. **Installation/Museum** (Public Access)
- Simple touch interface with limited controls
- Auto-reset after inactivity
- Child-safe interaction patterns

---

## 🔮 **Future Extensions**

### Advanced Ring Mask Features
1. **Pattern Presets**: Save/load ring visibility patterns
2. **Animation Sequences**: Automated ring reveals over time
3. **Audio-Reactive Masking**: Rings appear/disappear with music
4. **Spatial Audio**: Ring position affects audio panning

### Enhanced Effects Rack
1. **Custom Effect Chains**: User-defined effect combinations
2. **Parameter Automation**: Effects that evolve over time
3. **Frequency-Specific**: Different effects for bass vs treble
4. **3D Space Effects**: Effects that interact with vessel geometry

The current system provides a solid foundation that can be extended for any use case while maintaining the core sacred geometry and signal processing principles.