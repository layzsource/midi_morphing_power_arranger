import asyncio
import json
import hashlib
from pathlib import Path

import pytest

from signal_form_split_servers_and_configs import collaborative_engine_server as ces


class DummyWebSocket:
    def __init__(self, name: str = "ws") -> None:
        self.name = name
        self.messages: list[dict] = []

    async def send_text(self, payload: str) -> None:
        self.messages.append(json.loads(payload))

    @property
    def last_message(self) -> dict | None:
        return self.messages[-1] if self.messages else None


def test_presence_events_broadcast_on_join_leave(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.create_session("test-session")
    session = manager.sessions[session_id]

    ws_one = DummyWebSocket("one")
    ws_two = DummyWebSocket("two")

    user_one = ces.User("user-one", ws_one, session_id)
    user_two = ces.User("user-two", ws_two, session_id)

    manager.add_user_to_session(user_one, session_id)
    manager.add_user_to_session(user_two, session_id)

    asyncio.run(
        session.broadcast_to_others(
            user_one.user_id,
            {
                "type": "collaborative_user_join",
                "user": user_one.to_dict(),
                "users_in_session": session.get_user_list(),
                "users_count": len(session.users),
                "timestamp": 123.0,
            },
        )
    )

    assert ws_two.last_message["type"] == "collaborative_user_join"
    assert ws_two.last_message["user"]["user_id"] == "user-one"
    assert ws_two.last_message["users_count"] == len(session.users)
    assert ws_two.last_message["user"]["color"] == user_one.color
    assert ws_one.last_message is None

    asyncio.run(
        session.broadcast_to_others(
            user_one.user_id,
            {
                "type": "collaborative_user_leave",
                "user_id": user_one.user_id,
                "username": user_one.username,
                "user_color": user_one.color,
                "users_in_session": [user_two.to_dict()],
                "users_count": len(session.users) - 1,
                "timestamp": 124.0,
            },
        )
    )
    assert ws_two.last_message["type"] == "collaborative_user_leave"
    assert ws_two.last_message["user_id"] == "user-one"
    assert ws_two.last_message["users_count"] == len(session.users) - 1
    assert ws_two.last_message["user_color"] == user_one.color


def test_cursor_updates_propagate_to_other_clients(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.add_user_to_session(ces.User("primary", DummyWebSocket("primary")))
    session = manager.sessions[session_id]

    ws_primary = session.users["primary"].websocket
    ws_peer = DummyWebSocket("peer")
    peer = ces.User("peer", ws_peer, session_id)
    manager.add_user_to_session(peer, session_id)

    asyncio.run(
        ces.handle_collaborative_message(
            "primary",
            {"type": "cursor_move", "x": 0.25, "y": 0.75},
        )
    )

    assert ws_peer.last_message["type"] == "cursor_update"
    assert ws_peer.last_message["user_id"] == "primary"
    assert ws_peer.last_message["x"] == pytest.approx(0.25)
    assert ws_peer.last_message["y"] == pytest.approx(0.75)
    assert ws_primary.messages == []


def test_session_ids_and_user_identity_are_stable():
    manager = ces.CollaborationManager()
    session_id = manager.add_user_to_session(ces.User("alpha", DummyWebSocket("alpha")))

    assert len(session_id) > 0
    assert manager.user_to_session["alpha"] == session_id

    user = manager.get_user("alpha")
    assert user.username.startswith("User_")
    assert user.color.startswith("#") and len(user.color) == 7

    repeat_user = ces.User("alpha", DummyWebSocket("alpha"))
    assert repeat_user.username == user.username
    assert repeat_user.color == user.color

    expected_color = f"#{hashlib.md5('alpha'.encode()).hexdigest()[:6]}"
    assert user.color == expected_color


def test_offline_session_contains_no_network_broadcasts(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)
    session_id = manager.add_user_to_session(ces.User("solo", DummyWebSocket("solo")))
    session = manager.sessions[session_id]

    asyncio.run(
        session.broadcast_to_others(
            "solo",
            {"type": "heartbeat", "timestamp": 999.0},
        )
    )

    solo_socket = session.users["solo"].websocket
    assert solo_socket.messages == []


def test_users_online_badge_logic_and_presence_toasts():
    frontend = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")

    assert 'id="users-online-badge"' in frontend
    assert "badge.style.display = 'inline'" in frontend
    assert "badge.style.display = 'none'" in frontend
    assert "countSpan.textContent = count" in frontend

    assert "showPresenceToast(`${data.user.username} joined`, 'join', data.user.color);" in frontend
    assert "showPresenceToast(`${data.username} left`, 'leave', data.user_color);" in frontend
    assert "function showPresenceToast(message, type = 'join', userColor = '#3b82f6')" in frontend
    assert ".presence-toast {" in frontend


def test_collaborative_sprite_interaction_payload(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.add_user_to_session(ces.User("initiator", DummyWebSocket("initiator")))
    session = manager.sessions[session_id]

    receiving_ws = DummyWebSocket("receiver")
    receiver = ces.User("receiver", receiving_ws, session_id)
    manager.add_user_to_session(receiver, session_id)

    asyncio.run(
        ces.handle_collaborative_message(
            "initiator",
            {
                "type": "sprite_interaction",
                "media_id": "portal_001",
                "interaction_type": "portal_click",
            },
        )
    )

    message = receiving_ws.last_message
    assert message["type"] == "collaborative_sprite_interaction"
    assert message["media_id"] == "portal_001"
    assert message["username"].startswith("User_")
    assert message["user_color"].startswith("#")


def test_collaborative_parameter_update_last_writer_wins(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.add_user_to_session(ces.User("writer", DummyWebSocket("writer")))
    session = manager.sessions[session_id]

    receiving_ws = DummyWebSocket("observer")
    observer = ces.User("observer", receiving_ws, session_id)
    manager.add_user_to_session(observer, session_id)

    async def send_updates():
        await ces.handle_collaborative_message(
            "writer",
            {"type": "parameter_change", "parameter": "zeta", "value": 0.2},
        )
        await ces.handle_collaborative_message(
            "writer",
            {"type": "parameter_change", "parameter": "zeta", "value": 0.9},
        )

    asyncio.run(send_updates())

    message = receiving_ws.last_message
    assert message["type"] == "collaborative_parameter_update"
    assert message["parameter"] == "zeta"
    assert message["value"] == 0.9
    assert message["user_color"].startswith("#")


def test_collaborative_chat_message_payload(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.add_user_to_session(ces.User("chatter", DummyWebSocket("chatter")))
    session = manager.sessions[session_id]

    receiving_ws = DummyWebSocket("audience")
    audience = ces.User("audience", receiving_ws, session_id)
    manager.add_user_to_session(audience, session_id)

    asyncio.run(
        ces.handle_collaborative_message(
            "chatter",
            {"type": "chat_message", "message": "Signal→Form live", "timestamp": 123456789},
        )
    )

    message = receiving_ws.last_message
    assert message["type"] == "collaborative_chat_message"
    assert message["message"] == "Signal→Form live"
    assert message["username"].startswith("User_")
    assert message["user_color"].startswith("#")
    assert "timestamp" in message


def test_collaborative_preset_applied_syncs_across_clients(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    session_id = manager.add_user_to_session(ces.User("preset-author", DummyWebSocket("author")))
    session = manager.sessions[session_id]

    receiving_ws = DummyWebSocket("listener")
    listener = ces.User("listener", receiving_ws, session_id)
    manager.add_user_to_session(listener, session_id)

    preset_payload = {"zeta": 0.42, "unity": 0.75}

    asyncio.run(
        ces.handle_collaborative_message(
            "preset-author",
            {
                "type": "preset_applied",
                "preset_name": "Spectral Glide",
                "preset_data": preset_payload,
            },
        )
    )

    message = receiving_ws.last_message
    assert message["type"] == "collaborative_preset_applied"
    assert message["preset_name"] == "Spectral Glide"
    assert message["preset_data"] == preset_payload
    assert message["user_id"] == "preset-author"
    assert message["user_color"].startswith("#")


def test_no_collaboration_payloads_when_session_missing(monkeypatch):
    manager = ces.CollaborationManager()
    monkeypatch.setattr(ces, "collaboration_manager", manager)

    user = ces.User("solo", DummyWebSocket("solo"))
    manager.add_user_to_session(user, "solo-session")

    monkeypatch.setattr(manager, "get_session", lambda _uid: None)
    monkeypatch.setattr(manager, "get_user", lambda _uid: None)

    asyncio.run(
        ces.handle_collaborative_message(
            "solo",
            {"type": "parameter_change", "parameter": "zeta", "value": 0.5},
        )
    )

    assert user.websocket.messages == []


def test_engine_telemetry_unaffected_by_collaboration_state():
    runner = ces.EngineRunner()
    telemetry_snapshot = runner.step()
    assert "S" in telemetry_snapshot
    assert "pmw" in telemetry_snapshot
    assert telemetry_snapshot["pmw"] == pytest.approx(0.5)
