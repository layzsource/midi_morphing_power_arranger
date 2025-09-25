Signal→Form Split — Ready-to-run Stubs

What’s here
-----------
1) engine_server.py  — WebSocket /telemetry + HTTP /control on :7070
2) encoder_stub.py   — /collection/home_cube, /atlas/home_cube.png, /stim/{id} on :7071
3) encoder_config.yaml
4) microfiche_config.json

How to run
----------
# Terminal 1: Engine
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn numpy scipy pillow
# Ensure engine.py exists in PYTHONPATH (or the fallback will run)
python engine_server.py

# Terminal 2: Encoder
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn pillow numpy
python encoder_stub.py --images ~/media/family_photos --videos ~/media/family_videos --cap 128

Microfiche (Claude) should connect to:
- WS telemetry: ws://localhost:7070/telemetry
- POST control: http://localhost:7070/control
- GET collection: http://localhost:7071/collection/home_cube
- GET atlas: http://localhost:7071/atlas/home_cube.png
- POST stim: http://localhost:7071/stim/{media_id}
