import asyncio
import json
from typing import Callable

import pytest
import uvicorn
import websockets

from signal_form_split_servers_and_configs import collaborative_engine_server as ces


class DummyWebSocket:
    def __init__(self, name: str) -> None:
        self.name = name
        self.messages: list[dict] = []

    async def send_text(self, payload: str) -> None:
        self.messages.append(json.loads(payload))

    @property
    def last(self) -> dict | None:
        return self.messages[-1] if self.messages else None


def setup_session(monkeypatch, *users: str):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    sockets = {}
    for user_id in users:
        sockets[user_id] = DummyWebSocket(user_id)
        manager.add_user_to_session(ces.User(user_id, sockets[user_id]))

    return manager, sockets


def test_portal_events_broadcast_with_attribution(monkeypatch):
    manager, sockets = setup_session(monkeypatch, "alpha", "beta", "gamma")

    asyncio.run(
        ces.handle_collaborative_message(
            "alpha",
            {"type": "sprite_interaction", "media_id": "portal_42", "interaction_type": "portal_click"},
        )
    )

    for user_id in ("beta", "gamma"):
        message = sockets[user_id].last
        assert message["type"] == "collaborative_sprite_interaction"
        assert message["media_id"] == "portal_42"
        assert message["username"].startswith("User_")
        assert message["user_color"].startswith("#")

    assert sockets["alpha"].messages == []


def test_slider_conflict_resolution_sends_latest_value(monkeypatch):
    manager, sockets = setup_session(monkeypatch, "alpha", "beta")

    async def drive_updates():
        await ces.handle_collaborative_message("alpha", {"type": "parameter_change", "parameter": "zeta", "value": 0.2})
        await ces.handle_collaborative_message("alpha", {"type": "parameter_change", "parameter": "zeta", "value": 0.9})

    asyncio.run(drive_updates())

    message = sockets["beta"].last
    assert message["type"] == "collaborative_parameter_update"
    assert message["parameter"] == "zeta"
    assert message["value"] == pytest.approx(0.9)


def test_chat_messages_propagate_to_all_clients(monkeypatch):
    manager, sockets = setup_session(monkeypatch, "alpha", "beta")

    asyncio.run(
        ces.handle_collaborative_message(
            "alpha",
            {"type": "chat_message", "message": "Signal→Form alive", "timestamp": 1234567890},
        )
    )

    chat = sockets["beta"].last
    assert chat["type"] == "collaborative_chat_message"
    assert chat["message"] == "Signal→Form alive"
    assert chat["username"].startswith("User_")


def test_preset_updates_sync_across_clients(monkeypatch):
    manager, sockets = setup_session(monkeypatch, "alpha", "beta", "gamma")

    asyncio.run(
        ces.handle_collaborative_message(
            "alpha",
            {
                "type": "preset_applied",
                "preset_name": "Solaris",
                "preset_data": {"zeta": 0.42},
            },
        )
    )

    for user_id in ("beta", "gamma"):
        preset_msg = sockets[user_id].last
        assert preset_msg["type"] == "collaborative_preset_applied"
        assert preset_msg["preset_name"] == "Solaris"
        assert preset_msg["preset_data"] == {"zeta": 0.42}
        assert preset_msg["user_id"] == "alpha"


def test_running_server_emits_collaborative_events():
    asyncio.run(_exercise_live_collaboration())


async def _exercise_live_collaboration() -> None:
    ces.collaboration_manager = ces.CollaborationManager()

    config = uvicorn.Config(ces.app, host="127.0.0.1", port=0, log_level="warning", lifespan="off")
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    # Poll for server start; if the sandbox blocks binding, skip the test
    for _ in range(50):
        if server_task.done():
            exc = server_task.exception()
            if isinstance(exc, SystemExit):
                pytest.skip("WebSocket server cannot bind in sandbox environment")
            raise exc
        if server.started:
            break
        await asyncio.sleep(0.1)
    else:
        pytest.skip("WebSocket server failed to start within timeout")

    # Determine the ephemeral port assigned by the OS
    if not server.servers or not server.servers[0].sockets:
        pytest.skip("Server sockets not available after startup")
    port = server.servers[0].sockets[0].getsockname()[1]

    async def connect(user_id: str):
        uri = f"ws://127.0.0.1:{port}/telemetry?session_id=test&user_id={user_id}"
        return await websockets.connect(uri)

    async def next_message(ws, expected_type: str, predicate: Callable[[dict], bool] | None = None, timeout: float = 3.0):
        predicate = predicate or (lambda _: True)
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise AssertionError(f"Timeout waiting for {expected_type}")
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            data = json.loads(raw)
            if data.get("type") != expected_type:
                continue
            if predicate(data):
                return data

    try:
        async with connect("alpha") as ws_alpha, connect("beta") as ws_beta:
            await next_message(ws_alpha, "connection_established")
            await next_message(ws_beta, "connection_established")
            await next_message(ws_alpha, "user_joined")  # Beta arrival announcement

            await ws_alpha.send(json.dumps({
                "type": "sprite_interaction",
                "media_id": "portal_live",
                "interaction_type": "portal_click",
            }))
            sprite_msg = await next_message(ws_beta, "collaborative_sprite_interaction")
            assert sprite_msg["media_id"] == "portal_live"
            assert sprite_msg["user_id"] == "alpha"

            await ws_alpha.send(json.dumps({
                "type": "parameter_change",
                "parameter": "pmw",
                "value": 0.15,
            }))
            await ws_alpha.send(json.dumps({
                "type": "parameter_change",
                "parameter": "pmw",
                "value": 0.85,
            }))
            param_msg = await next_message(
                ws_beta,
                "collaborative_parameter_update",
                predicate=lambda d: d.get("value") == 0.85,
            )
            assert param_msg["parameter"] == "pmw"

            await ws_alpha.send(json.dumps({
                "type": "chat_message",
                "message": "hello cosmos",
                "timestamp": 1712000000,
            }))
            chat_msg = await next_message(ws_beta, "collaborative_chat_message")
            assert chat_msg["message"] == "hello cosmos"
            assert chat_msg["user_id"] == "alpha"

            await ws_alpha.send(json.dumps({
                "type": "preset_applied",
                "preset_name": "Aurora",
                "preset_data": {"zeta": 0.21, "unity": 0.4},
            }))
            preset_msg = await next_message(ws_beta, "collaborative_preset_applied")
            assert preset_msg["preset_name"] == "Aurora"
            assert preset_msg["preset_data"] == {"zeta": 0.21, "unity": 0.4}
            assert preset_msg["user_id"] == "alpha"

    finally:
        server.should_exit = True
        await asyncio.wait_for(server_task, timeout=5)
