#!/bin/bash
set -euo pipefail

# Cleanup function to kill all background processes
cleanup() {
    echo ""
    echo "🛑 Cleaning up services..."
    kill 0 2>/dev/null || true
    echo "✅ All services stopped"
}

# Trap EXIT to ensure cleanup on script termination
trap cleanup EXIT

echo "🌊 Signal→Form Engine: Starting All Services"
echo "=============================================="

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "📦 Using existing virtual environment"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install required packages
echo "📥 Installing Python packages..."
pip install --quiet fastapi uvicorn numpy scipy pillow pytest

# Change to server directory
cd signal_form_split_servers_and_configs

# Launch engine server (port 7070)
echo "🚀 Starting Engine Server (port 7070)..."
python3 engine_server.py &
ENGINE_PID=$!
echo "✅ Engine Server started (PID: $ENGINE_PID)"

# Wait a moment for engine to start
sleep 2

# Launch encoder stub (port 7071)
echo "🚀 Starting Encoder Server (port 7071)..."
python3 encoder_stub.py --images ~/Downloads --cap 128 &
ENCODER_PID=$!
echo "✅ Encoder Server started (PID: $ENCODER_PID)"

# Wait a moment for encoder to start
sleep 3

# Go back to project root and open browser
cd ..
echo "🌐 Opening Spherical POV Interface..."
open microfiche/index.html

echo ""
echo "🎉 All services running!"
echo "=============================================="
echo "📊 Engine Server:    http://localhost:7070"
echo "🗂️  Encoder Server:   http://localhost:7071"
echo "🌊 Spherical POV:    microfiche/index.html"
echo ""
echo "💡 Usage:"
echo "   • Mouse wheel: Zoom ζ (outside→inside)"
echo "   • Mouse drag: Orbit camera"
echo "   • Click sprites: Portal events"
echo "   • CENTER ME: Emergency grounding"
echo ""
echo "🛑 To stop all services:"
echo "   Press Ctrl+C or close terminal"
echo ""
echo "📝 Check WebSocket status in browser HUD"
echo "   Should show 'Connected' when ready"

# Keep script running and show PIDs
echo "⚡ Services running with PIDs: Engine=$ENGINE_PID, Encoder=$ENCODER_PID"
echo "   Press Ctrl+C to stop all services and exit"

# Wait for user interrupt
wait