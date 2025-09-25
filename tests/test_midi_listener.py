import asyncio
import json

import mido
import pytest

from scripts import midi_listener as ml


class DummyTask:
    def __init__(self, coro):
        self.coro = coro
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True

    def __await__(self):
        async def _noop():
            return None

        return _noop().__await__()


def test_startup_falls_back_to_synthetic_mode(monkeypatch):
    monkeypatch.setattr(ml.mido, "get_input_names", lambda: [])

    created = {}

    def fake_create_task(coro):
        created["task"] = DummyTask(coro)
        return created["task"]

    monkeypatch.setattr(ml.asyncio, "create_task", fake_create_task)

    asyncio.run(ml.start_background_tasks())
    assert ml.app.state.mode == "synthetic"
    assert created["task"].coro.__name__ == "broadcast_loop"

    asyncio.run(ml.stop_background_tasks())
    created["task"].coro.close()


def test_startup_uses_real_midi_when_available(monkeypatch):
    monkeypatch.setattr(ml.mido, "get_input_names", lambda: ["Fake MIDI"])

    observed = {}

    def fake_create_task(coro):
        observed["task"] = DummyTask(coro)
        return observed["task"]

    class FakePort:
        def close(self):
            observed["closed"] = True

    def fake_open_input(name, callback=None):
        observed["callback"] = callback
        observed["opened"] = name
        return FakePort()

    monkeypatch.setattr(ml.asyncio, "create_task", fake_create_task)
    monkeypatch.setattr(ml.mido, "open_input", fake_open_input)

    asyncio.run(ml.start_background_tasks())
    assert ml.app.state.mode == "real"
    assert observed["opened"] == "Fake MIDI"
    assert observed["task"].coro.__name__ == "real_midi_loop"

    asyncio.run(ml.stop_background_tasks())
    assert observed.get("closed") is True
    observed["task"].coro.close()


def test_broadcast_loop_emits_synthetic_events(monkeypatch):
    events = []

    async def fake_broadcast(message):
        events.append(json.loads(message))
        raise asyncio.CancelledError

    monkeypatch.setattr(ml.manager, "broadcast", fake_broadcast)

    async def runner():
        with pytest.raises(asyncio.CancelledError):
            await ml.broadcast_loop()

    asyncio.run(runner())

    event = events[0]
    assert event["param"] in ml.PARAM_SEQUENCE
    assert event["value"] == pytest.approx(0.5)


def test_real_midi_loop_emits_control_change(monkeypatch):
    events = []

    async def fake_broadcast(message):
        events.append(json.loads(message))
        raise asyncio.CancelledError

    monkeypatch.setattr(ml.manager, "broadcast", fake_broadcast)

    async def runner():
        queue: asyncio.Queue[mido.Message] = asyncio.Queue()
        await queue.put(mido.Message("control_change", control=21, value=64, channel=2))
        with pytest.raises(asyncio.CancelledError):
            await ml.real_midi_loop(queue)

    asyncio.run(runner())

    event = events[0]
    assert event["type"] == "cc"
    assert event["control"] == 21
    assert event["value"] == 64
