import asyncio
import websockets
import json

async def midi_handler(ws, path):
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

async def main():
    print("🎹 MIDI stub listening on ws://localhost:7072/midi")
    async with websockets.serve(midi_handler, "0.0.0.0", 7072):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
