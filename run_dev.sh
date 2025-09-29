#!/bin/bash
# Simple dev launcher for MIDI Morphing Interface

# Kill anything still running on these ports (macOS compatible)
echo "🧹 Cleaning up existing processes..."
lsof -ti :7070 | xargs kill -9 2>/dev/null || true
lsof -ti :7072 | xargs kill -9 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

# Change to script directory
cd "$(dirname "$0")"

# 1. Start static file server for index_latest.html + JSON configs
echo "📂 Starting HTTP server on http://localhost:8000/"
python3 -m http.server 8000 &
HTTP_PID=$!

# 2. Start telemetry WebSocket server (port 7070)
echo "📊 Starting telemetry stub on ws://localhost:7070"
python3 telemetry_stub.py &
TEL_PID=$!

# 3. Start MIDI WebSocket server (port 7072)
echo "🎹 Starting MIDI stub on ws://localhost:7072/midi"
python3 midi_stub.py &
MIDI_PID=$!

# 4. Wait for servers to start then open browser
sleep 2
echo "🌐 Opening browser..."
open "http://localhost:8000/index_latest.html"

echo "✅ All services running:"
echo "   📂 HTTP: http://localhost:8000"
echo "   📊 Telemetry: ws://localhost:7070"
echo "   🎹 MIDI: ws://localhost:7072/midi"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $HTTP_PID $TEL_PID $MIDI_PID 2>/dev/null || true
    lsof -ti :7070 | xargs kill -9 2>/dev/null || true
    lsof -ti :7072 | xargs kill -9 2>/dev/null || true
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    echo "✅ Cleanup complete"
}
trap cleanup EXIT

# Wait for all background processes
wait