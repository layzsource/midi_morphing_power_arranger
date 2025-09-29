import asyncio
import websockets
import json
import random
import time

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

async def main():
    print("📊 Telemetry stub listening on ws://localhost:7070")
    async with websockets.serve(telemetry_handler, "0.0.0.0", 7070):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
