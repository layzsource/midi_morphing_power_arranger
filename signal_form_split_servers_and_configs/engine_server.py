# engine_server.py
# Unified Engine server: WebSocket /telemetry + HTTP /control
# Requires: fastapi, uvicorn, numpy, scipy
# Run:
#   pip install fastapi uvicorn numpy scipy
#   python engine_server.py
import asyncio, json, math
from typing import Dict, Any, List
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

@app.get("/", response_class=PlainTextResponse)
def root(): return "Engine Server OK. WS: /telemetry  POST /control"

@app.websocket("/telemetry")
async def telemetry(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            tel = runner.step()
            await ws.send_text(json.dumps(tel))
            await asyncio.sleep(1.0/FPS)
    except WebSocketDisconnect:
        pass

@app.post("/control")
async def control(body: Dict[str, Any]):
    setv = body.get("set", {})
    if "pmw" in setv: runner.pmw = float(setv["pmw"])
    p = body.get("pulse")
    if p: runner.add_pulse(p.get("k",0), p.get("amp",0.5), p.get("decay",0.95))
    return {"ok": True, "pmw": runner.pmw, "pulses": len(runner._pulses)}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
