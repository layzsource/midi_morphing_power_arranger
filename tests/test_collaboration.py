import asyncio
import json
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


def test_engine_telemetry_unaffected_by_collaboration_state():
    runner = ces.EngineRunner()
    telemetry_snapshot = runner.step()
    assert "S" in telemetry_snapshot
    assert "pmw" in telemetry_snapshot
    assert telemetry_snapshot["pmw"] == pytest.approx(0.5)
