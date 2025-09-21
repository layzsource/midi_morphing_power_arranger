# MMPA Ableton Live Integration

## Max for Live Device Setup

To enable Ableton Live integration with MMPA, you need to create a Max for Live device that streams audio and MIDI data via WebSocket.

### Required Max for Live Objects:

```
1. [live.remote~] - For audio output capture
2. [live.path] - For transport and tempo info
3. [udpsend] or [node.script] - For WebSocket communication
4. [metro] - For timing
5. [buffer~] - For audio buffering
```

### Max Patch Structure:

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   live.remote~  │───▶│   buffer~    │───▶│  WebSocket Send │
│  (master out)   │    │ (audio data) │    │ (to MMPA app)   │
└─────────────────┘    └──────────────┘    └─────────────────┘
        │
        ▼
┌─────────────────┐    ┌──────────────┐
│   live.path     │───▶│ Format JSON  │
│ (tempo/trans.)  │    │  Messages    │
└─────────────────┘    └──────────────┘
```

### WebSocket Protocol:

#### Audio Stream Message:
```json
{
  "type": "audio_data",
  "timestamp": 1234567890,
  "sampleRate": 44100,
  "channels": 2,
  "data": [0.1, -0.2, 0.3, ...] // Float32Array as array
}
```

#### Tempo Message:
```json
{
  "type": "tempo",
  "timestamp": 1234567890,
  "tempo": 120.0,
  "timeSignature": [4, 4]
}
```

#### Transport Message:
```json
{
  "type": "transport",
  "timestamp": 1234567890,
  "state": "playing", // "playing", "stopped", "paused"
  "position": 16.0,   // Beat position
  "bars": 4,
  "beats": 1,
  "sixteenths": 1
}
```

### Max for Live Patch Code Example:

```max
// Main patch structure
autowatch 1;

inlets = 2; // Audio in (L, R)
outlets = 1; // WebSocket out

var websocket;
var isConnected = false;

function loadbang() {
    // Initialize WebSocket connection
    websocket = new WebSocket("ws://localhost:8081");

    websocket.onopen = function() {
        isConnected = true;
        post("MMPA WebSocket connected");
    };

    websocket.onerror = function(error) {
        post("WebSocket error:", error);
        isConnected = false;
    };
}

function signal(channel, samples) {
    if (!isConnected) return;

    // Send audio data every 1024 samples (adjust for latency vs. bandwidth)
    if (samples.length >= 1024) {
        var message = {
            type: "audio_data",
            timestamp: Date.now(),
            sampleRate: 44100,
            channels: 2,
            data: Array.from(samples)
        };

        websocket.send(JSON.stringify(message));
    }
}

function tempo(bpm) {
    if (!isConnected) return;

    var message = {
        type: "tempo",
        timestamp: Date.now(),
        tempo: bpm,
        timeSignature: [4, 4] // Could be dynamic
    };

    websocket.send(JSON.stringify(message));
}

function transport(state, position) {
    if (!isConnected) return;

    var message = {
        type: "transport",
        timestamp: Date.now(),
        state: state,
        position: position
    };

    websocket.send(JSON.stringify(message));
}
```

### Installation Instructions:

1. **Install Max for Live** (requires Ableton Live Suite or Standard + Max for Live)

2. **Create the Device:**
   - Open Max for Live
   - Create new Audio Effect
   - Build the patch using the structure above
   - Save as "MMPA_Bridge.amxd"

3. **Install in Ableton:**
   - Place the .amxd file in your User Library
   - Drag onto the Master track
   - The device will auto-connect to MMPA when both are running

4. **WebSocket Server:**
   - MMPA automatically starts a WebSocket server on port 8081
   - The Max device connects to ws://localhost:8081
   - Audio data is streamed in real-time with minimal latency

### Features:

- **Real-time audio streaming** from Ableton to MMPA
- **Tempo synchronization** - MMPA visuals sync to Ableton's tempo
- **Transport control** - Play/stop states shared between apps
- **Low latency** - Optimized for live performance
- **Automatic reconnection** - Handles disconnections gracefully

### Troubleshooting:

- **Connection fails:** Ensure MMPA is running first
- **Audio dropouts:** Reduce buffer size in Max patch
- **High CPU usage:** Increase audio chunk size
- **No audio:** Check Ableton's audio routing and levels

### Alternative: OSC Integration

If WebSocket proves problematic, MMPA also supports OSC:

```javascript
// OSC endpoint: /mmpa/audio
// Port: 8000
// Format: /mmpa/audio <channel> <sample1> <sample2> ...
```

This Max for Live bridge creates a seamless connection between Ableton Live and MMPA, allowing DJs and producers to use MMPA as a real-time visual instrument driven by their DAW.