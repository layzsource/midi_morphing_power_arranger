"""Synthetic MIDI WebSocket broadcaster served via FastAPI."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import time
from itertools import cycle
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import mido

HOST = "0.0.0.0"
PORT = 7072
ENDPOINT = "/midi"
INTERVAL_SECONDS = 2.0
PARAM_SEQUENCE = ("zeta", "unity", "flatness")

logger = logging.getLogger("signal_form.midi.listener")

app = FastAPI(title="Signal→Form Synthetic MIDI", version="0.1.0")


class ConnectionManager:
    """Track active WebSocket connections and broadcast messages."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info("Client connected from %s", websocket.client)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)
        logger.info("Client disconnected from %s", websocket.client)

    async def broadcast(self, message: str) -> None:
        async with self._lock:
            connections = list(self._connections)
        if not connections:
            return
        stale: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                stale.append(websocket)
            except Exception as exc:  # pragma: no cover - defensive
                logger.warning("Failed to send to %s: %s", websocket.client, exc)
                stale.append(websocket)
        if stale:
            async with self._lock:
                for websocket in stale:
                    self._connections.discard(websocket)


manager = ConnectionManager()


def build_payload(param: str) -> str:
    return json.dumps(
        {
            "timestamp": int(time.time()),
            "param": param,
            "value": 0.5,
            "value_norm": 0.5,
        }
    )


async def broadcast_loop() -> None:
    params = cycle(PARAM_SEQUENCE)
    try:
        while True:
            message = build_payload(next(params))
            await manager.broadcast(message)
            await asyncio.sleep(INTERVAL_SECONDS)
    except asyncio.CancelledError:  # pragma: no cover - shutdown path
        logger.info("Broadcast loop cancelled")
        raise


def build_midi_payload(message: mido.Message) -> str | None:
    if message.type != "control_change":
        return None
    value = int(message.value)
    return json.dumps(
        {
            "timestamp": int(time.time()),
            "type": "cc",
            "control": int(message.control),
            "value": value,
            "midi": {
                "channel": int(getattr(message, "channel", 0)),
                "cc": int(message.control),
                "value": value,
            },
            "value_norm": value / 127.0,
        }
    )


async def real_midi_loop(queue: "asyncio.Queue[mido.Message]") -> None:
    try:
        while True:
            message = await queue.get()
            payload = build_midi_payload(message)
            if payload is None:
                continue
            await manager.broadcast(payload)
    except asyncio.CancelledError:  # pragma: no cover - shutdown path
        logger.info("Real MIDI loop cancelled")
        raise


@app.websocket(ENDPOINT)
async def midi_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("WebSocket error: %s", exc)
        await manager.disconnect(websocket)


@app.on_event("startup")
async def start_background_tasks() -> None:
    loop = asyncio.get_running_loop()
    midi_names: list[str] = []
    try:
        midi_names = list(mido.get_input_names())
    except Exception as exc:  # pragma: no cover - hardware/env specific
        logger.warning("Unable to enumerate MIDI inputs: %s", exc)

    if midi_names:
        port_name = midi_names[0]
        logger.info(
            "Starting MIDI broadcaster in REAL MIDI mode on ws://%s:%d%s (port=%s)",
            HOST,
            PORT,
            ENDPOINT,
            port_name,
        )
        queue: asyncio.Queue[mido.Message] = asyncio.Queue()

        def callback(message: mido.Message) -> None:
            if message.type != "control_change":  # filter non-CC events early
                return
            loop.call_soon_threadsafe(queue.put_nowait, message)

        try:
            port = mido.open_input(port_name, callback=callback)
        except OSError as exc:  # pragma: no cover - hardware failure
            logger.warning(
                "Failed to open MIDI input '%s' (%s); falling back to SYNTHETIC mode",
                port_name,
                exc,
            )
            port = None
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Unexpected error opening MIDI input '%s' (%s); falling back to SYNTHETIC mode",
                port_name,
                exc,
            )
            port = None

        if port is not None:
            app.state.mode = "real"
            app.state.midi_port = port
            app.state.broadcast_task = asyncio.create_task(real_midi_loop(queue))
            return

    logger.info(
        "Starting MIDI broadcaster in SYNTHETIC mode on ws://%s:%d%s", HOST, PORT, ENDPOINT
    )
    app.state.mode = "synthetic"
    app.state.midi_port = None
    app.state.broadcast_task = asyncio.create_task(broadcast_loop())


@app.on_event("shutdown")
async def stop_background_tasks() -> None:
    task: asyncio.Task | None = getattr(app.state, "broadcast_task", None)
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
    port = getattr(app.state, "midi_port", None)
    if port:
        port.close()


def main() -> None:  # pragma: no cover - CLI entrypoint
    import uvicorn

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
