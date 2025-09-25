# collaborative_engine_server.py
# Extended Engine server with collaborative features
# Requires: fastapi, uvicorn, numpy, scipy
# Run:
#   pip install fastapi uvicorn numpy scipy
#   python collaborative_engine_server.py
import asyncio, json, math, time, uuid
from typing import Dict, Any, List, Set
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
import uvicorn

try:
    from engine import GraphConfig, EngineConfig, SignalFormEngine
except Exception:
    # Minimal fallback engine if engine.py isn't present
    GraphConfig = object
    EngineConfig = object
    class SignalFormEngine:
        def __init__(self, *a, **k): self.K=32; self.modes=np.eye(32); self._t=0.0
        def step(self, s, kx=1, ky=2):
            self._t+=1/60
            c = np.fft.rfft(s)[:self.K]
            S = {"U":0.5,"F":0.5,"blend":0.5}
            return {"S":S,"stokes":{"S0":1,"S1":0,"S2":0,"S3":0,"pair":[1,2]},
                    "entropy":0.4,"R":float(np.random.rand()),
                    "green":{"x0":0,"t":0.12,"summary":{"radius":12}},
                    "lambdas":[0]*8}

HOST="0.0.0.0"; PORT=7070; FPS=60.0

# Collaborative Session Management
class User:
    def __init__(self, user_id: str, websocket: WebSocket, session_id: str = None):
        self.user_id = user_id
        self.websocket = websocket
        self.session_id = session_id or "default"
        self.username = f"User_{user_id[:6]}"
        self.color = self._generate_color()
        self.cursor_x = 0.5
        self.cursor_y = 0.5
        self.last_activity = time.time()
        self.connected_at = time.time()

    def _generate_color(self):
        """Generate a consistent color based on user_id"""
        import hashlib
        hash_obj = hashlib.md5(self.user_id.encode())
        hash_hex = hash_obj.hexdigest()
        # Use first 6 chars as RGB hex
        return f"#{hash_hex[:6]}"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color,
            "cursor_x": self.cursor_x,
            "cursor_y": self.cursor_y,
            "session_id": self.session_id,
            "connected_at": self.connected_at
        }

class CollaborativeSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.users: Dict[str, User] = {}
        self.created_at = time.time()
        self.last_activity = time.time()

    def add_user(self, user: User):
        self.users[user.user_id] = user
        self.last_activity = time.time()

    def remove_user(self, user_id: str):
        if user_id in self.users:
            del self.users[user_id]
            self.last_activity = time.time()

    def get_user_list(self):
        return [user.to_dict() for user in self.users.values()]

    async def broadcast_to_others(self, sender_id: str, message: dict):
        """Broadcast message to all users in session except sender"""
        for user_id, user in self.users.items():
            if user_id != sender_id:
                try:
                    await user.websocket.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Failed to send to user {user_id}: {e}")

    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all users in session"""
        for user_id, user in self.users.items():
            try:
                await user.websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Failed to broadcast to user {user_id}: {e}")

class CollaborationManager:
    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.user_to_session: Dict[str, str] = {}

    def create_session(self, session_id: str = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        if session_id not in self.sessions:
            self.sessions[session_id] = CollaborativeSession(session_id)

        return session_id

    def add_user_to_session(self, user: User, session_id: str = None) -> str:
        if not session_id:
            session_id = "default"

        # Ensure session exists
        if session_id not in self.sessions:
            self.create_session(session_id)

        user.session_id = session_id
        self.sessions[session_id].add_user(user)
        self.user_to_session[user.user_id] = session_id

        print(f"👤 User {user.username} joined session {session_id}")
        return session_id

    def remove_user(self, user_id: str):
        if user_id in self.user_to_session:
            session_id = self.user_to_session[user_id]
            if session_id in self.sessions:
                user = self.sessions[session_id].users.get(user_id)
                if user:
                    print(f"👋 User {user.username} left session {session_id}")
                self.sessions[session_id].remove_user(user_id)

                # Clean up empty sessions
                if not self.sessions[session_id].users:
                    del self.sessions[session_id]
                    print(f"🗑️ Session {session_id} closed (empty)")

            del self.user_to_session[user_id]

    def get_session(self, user_id: str) -> CollaborativeSession:
        session_id = self.user_to_session.get(user_id)
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        return None

    def get_user(self, user_id: str) -> User:
        session = self.get_session(user_id)
        if session:
            return session.users.get(user_id)
        return None

def ring_lattice(n: int, k: int = 2, w: float = 1.0):
    edges = []
    for i in range(n):
        for d in range(1, k+1):
            j1 = (i + d) % n
            j2 = (i - d) % n
            edges.append((i, j1, w))
            edges.append((i, j2, w))
    return edges

class EngineRunner:
    def __init__(self, n=256, K=32, x0=0, t_heat=0.12):
        try:
            gcfg = GraphConfig(nodes=n, edges=ring_lattice(n), normalized=True)
            ecfg = EngineConfig(K=K, x0=x0, t_heat=t_heat, alpha_white=0.5, smooth=0.2)
            self.eng = SignalFormEngine(gcfg, ecfg)
            self.K = K
        except Exception:
            self.eng = SignalFormEngine()
            self.K = getattr(self.eng, "K", 32)
        self.dt = 1.0/FPS
        self.omega = 2*math.pi*0.2
        self.phi = 0.0
        self.active_modes = [0,1,2,5,8,13]
        self.amps = np.linspace(1.0, 0.2, num=len(self.active_modes))
        self.t = 0.0
        self.pmw = 0.5
        self._pulses: List[Dict[str, Any]] = []

    def add_pulse(self, k:int, amp:float, decay:float):
        self._pulses.append({"k": max(0, min(int(k), self.K-1)), "amp": float(amp), "decay": float(decay), "ttl": 1.0})

    def step(self):
        # synthetic modal vector
        c = np.zeros(self.K, dtype=np.complex128)
        self.phi += self.omega*self.dt
        for a_idx, k_idx in enumerate(self.active_modes):
            mag = self.amps[a_idx] * (0.75 + 0.25*math.sin(self.phi + a_idx))
            phase = self.phi*(1+a_idx*0.1)
            c[k_idx] = mag * complex(math.cos(phase), math.sin(phase))
        for p in list(self._pulses):
            k=p["k"]; c[k] += p["amp"]*p["ttl"]; p["ttl"] *= p["decay"]
            if p["ttl"]<1e-3: self._pulses.remove(p)
        c[0] += 0.3*self.pmw
        # project back to a node field to feed engine
        s = np.real(np.fft.irfft(np.pad(c, (0, max(0, 64-len(c))), constant_values=0)))[:64]
        tel = self.eng.step(s, kx=1, ky=2)
        tel["pmw"] = self.pmw; tel["time"] = self.t
        self.t += self.dt
        return tel

app = FastAPI()
runner = EngineRunner()
collaboration_manager = CollaborationManager()

@app.get("/", response_class=PlainTextResponse)
def root(): return "Collaborative Engine Server OK. WS: /telemetry  POST /control"

@app.websocket("/telemetry")
async def telemetry(ws: WebSocket, session_id: str = None, user_id: str = None):
    await ws.accept()

    # Generate user ID if not provided
    if not user_id:
        user_id = str(uuid.uuid4())

    # Create user and add to session
    user = User(user_id, ws, session_id)
    actual_session_id = collaboration_manager.add_user_to_session(user, session_id)
    session = collaboration_manager.get_session(user_id)

    # Send initial connection confirmation
    await ws.send_text(json.dumps({
        "type": "connection_established",
        "user_info": user.to_dict(),
        "session_id": actual_session_id,
        "timestamp": time.time()
    }))

    # Notify other users in session about new connection
    if session:
        await session.broadcast_to_others(user_id, {
            "type": "collaborative_user_join",
            "user": user.to_dict(),
            "users_in_session": session.get_user_list(),
            "users_count": len(session.users),
            "timestamp": time.time()
        })

        # Also send the legacy event for backward compatibility
        await session.broadcast_to_others(user_id, {
            "type": "user_joined",
            "user": user.to_dict(),
            "users_in_session": session.get_user_list(),
            "timestamp": time.time()
        })

    try:
        # Start telemetry and message handling
        async def send_telemetry():
            while True:
                tel = runner.step()
                tel["type"] = "telemetry"
                tel["session_id"] = actual_session_id

                # Add collaborative info
                if session:
                    tel["collaboration"] = {
                        "users_count": len(session.users),
                        "session_id": actual_session_id
                    }

                await ws.send_text(json.dumps(tel))
                await asyncio.sleep(1.0/FPS)

        async def handle_messages():
            while True:
                try:
                    data = await ws.receive_text()
                    message = json.loads(data)
                    await handle_collaborative_message(user_id, message)
                except Exception as e:
                    print(f"Message handling error: {e}")
                    break

        # Run both tasks concurrently
        await asyncio.gather(send_telemetry(), handle_messages())

    except WebSocketDisconnect:
        pass
    finally:
        # Clean up user on disconnect
        if session:
            remaining_users = [u.to_dict() for u in session.users.values() if u.user_id != user_id]
            await session.broadcast_to_others(user_id, {
                "type": "collaborative_user_leave",
                "user_id": user_id,
                "username": user.username,
                "user_color": user.color,
                "users_in_session": remaining_users,
                "users_count": len(remaining_users),
                "timestamp": time.time()
            })

            # Also send the legacy event for backward compatibility
            await session.broadcast_to_others(user_id, {
                "type": "user_left",
                "user_id": user_id,
                "username": user.username,
                "users_in_session": remaining_users,
                "timestamp": time.time()
            })

        collaboration_manager.remove_user(user_id)

async def handle_collaborative_message(user_id: str, message: dict):
    """Handle collaborative messages from clients"""
    session = collaboration_manager.get_session(user_id)
    user = collaboration_manager.get_user(user_id)

    if not session or not user:
        return

    message_type = message.get("type")

    if message_type == "cursor_move":
        # Update user cursor position and broadcast to others
        user.cursor_x = max(0.0, min(1.0, float(message.get("x", 0.5))))
        user.cursor_y = max(0.0, min(1.0, float(message.get("y", 0.5))))
        user.last_activity = time.time()

        await session.broadcast_to_others(user_id, {
            "type": "cursor_update",
            "user_id": user_id,
            "username": user.username,
            "color": user.color,
            "x": user.cursor_x,
            "y": user.cursor_y,
            "timestamp": time.time()
        })

    elif message_type == "parameter_change":
        # Broadcast parameter changes from one user to others
        await session.broadcast_to_others(user_id, {
            "type": "collaborative_parameter_update",
            "user_id": user_id,
            "username": user.username,
            "user_color": user.color,
            "parameter": message.get("parameter"),
            "value": message.get("value"),
            "source": message.get("source", "unknown"),
            "timestamp": time.time()
        })

    elif message_type == "sprite_interaction":
        # Broadcast sprite interactions
        await session.broadcast_to_others(user_id, {
            "type": "collaborative_sprite_interaction",
            "user_id": user_id,
            "username": user.username,
            "user_color": user.color,
            "media_id": message.get("media_id"),
            "interaction_type": message.get("interaction_type", "click"),
            "timestamp": time.time()
        })

    elif message_type == "preset_applied":
        # Broadcast preset applications
        await session.broadcast_to_others(user_id, {
            "type": "collaborative_preset_applied",
            "user_id": user_id,
            "username": user.username,
            "user_color": user.color,
            "preset_name": message.get("preset_name"),
            "preset_data": message.get("preset_data"),
            "timestamp": time.time()
        })

    elif message_type == "chat_message":
        # Broadcast chat messages
        await session.broadcast_to_others(user_id, {
            "type": "collaborative_chat_message",
            "user_id": user_id,
            "username": user.username,
            "user_color": user.color,
            "message": message.get("message"),
            "timestamp": message.get("timestamp", time.time() * 1000)  # Convert to milliseconds
        })

@app.post("/control")
async def control(body: Dict[str, Any]):
    setv = body.get("set", {})
    if "pmw" in setv: runner.pmw = float(setv["pmw"])
    p = body.get("pulse")
    if p: runner.add_pulse(p.get("k",0), p.get("amp",0.5), p.get("decay",0.95))
    return {"ok": True, "pmw": runner.pmw, "pulses": len(runner._pulses)}

if __name__ == "__main__":
    print("🤝 Starting Collaborative Engine Server...")
    print(f"📡 WebSocket: ws://{HOST}:{PORT}/telemetry")
    print(f"🎛️ Control: http://{HOST}:{PORT}/control")
    print("📋 Usage: Add ?session_id=your_session&user_id=your_id to WebSocket URL")
    uvicorn.run(app, host=HOST, port=PORT)