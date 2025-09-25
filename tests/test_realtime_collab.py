import asyncio
import json

import pytest

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
