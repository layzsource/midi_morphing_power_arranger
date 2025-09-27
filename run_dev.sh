#!/bin/bash
# Simple dev launcher for MIDI Morphing Interface

# Kill anything still running on these ports
fuser -k 7070/tcp 2>/dev/null
fuser -k 7072/tcp 2>/dev/null

# 1. Start static file server for index_latest.html + JSON configs
echo "📂 Serving project at http://localhost:8000/"
cd "$(dirname "$0")"
python3 -m http.server 8000 &
HTTP_PID=$!

# 2. Start stub WebSocket server for telemetry (port 7070)
cat > telemetry_stub.py <<'EOF'
import asyncio, websockets, json, random, time

async def telemetry_handler(ws, path):
    print("📊 Telemetry client connected")
    try:
        while True:
            payload = {
                "timestamp": int(time.time()),
                "signal_strength": round(random.uniform(0.5, 1.0), 2),
                "latency": random.randint(5, 20),
                "frame": random.randint(1, 9999),
                "status": "active",
                "channels": {
                    "midi": round(random.uniform(0.0, 1.0), 3),
                    "audio": round(random.uniform(0.0, 1.0), 3),
                    "visual": round(random.uniform(0.0, 1.0), 3)
                }
            }
            await ws.send(json.dumps(payload))
            print(f"📊 Telemetry broadcast → {payload}")
            await asyncio.sleep(1)
    except websockets.ConnectionClosed:
        print("📊 Telemetry client disconnected")
    except Exception as e:
        print(f"📊 Telemetry handler error: {e}")

print("📊 Telemetry stub listening on ws://localhost:7070")
asyncio.get_event_loop().run_until_complete(
    websockets.serve(telemetry_handler, "0.0.0.0", 7070)
)
asyncio.get_event_loop().run_forever()
EOF
python3 telemetry_stub.py &
TEL_PID=$!

# 3. Start stub WebSocket server for MIDI (port 7072)
cat > midi_stub.py <<'EOF'
import asyncio, websockets, json
async def handler(ws, path):
    print("🎹 MIDI client connected")
    try:
        async for message in ws:
            print(f"🎹 MIDI received: {message}")
            try:
                # Echo back as JSON
                echo_response = json.dumps({"echo": message})
                await ws.send(echo_response)
                print(f"🎹 MIDI echoed: {echo_response}")
            except Exception as e:
                print(f"🎹 MIDI echo error: {e}")
    except websockets.ConnectionClosed:
        print("🎹 MIDI client disconnected")
    except Exception as e:
        print(f"🎹 MIDI handler error: {e}")

print("🎹 MIDI stub listening on ws://localhost:7072/midi")
asyncio.get_event_loop().run_until_complete(
    websockets.serve(handler, "0.0.0.0", 7072)
)
asyncio.get_event_loop().run_forever()
EOF
python3 midi_stub.py &
MIDI_PID=$!

# 4. Open browser
sleep 1
open "http://localhost:8000/index_latest.html"

# Cleanup on exit
trap "kill $HTTP_PID $TEL_PID $MIDI_PID" EXIT
wait