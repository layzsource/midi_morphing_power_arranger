import re
from pathlib import Path

import pytest

HTML_PATH = Path(__file__).resolve().parents[1] / "microfiche" / "index.html"
HTML_SOURCE = HTML_PATH.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "pattern",
    [
        r"new\s+BroadcastChannel\('signal-form-sync'\)",
        r"function\s+handleRemoteParameterUpdate\(data\)",
        r"case 'zeta':.*updateCamera\(\);.*updateShells\(\);",
        r"broadcastChannel\.postMessage\(message\)",
        r"broadcastUpdate\('window_heartbeat'",
    ],
)
def test_broadcast_channel_parameter_sync(pattern: str) -> None:
    assert re.search(pattern, HTML_SOURCE, flags=re.DOTALL), pattern


def test_camera_sync_respects_idle_windows() -> None:
    pattern = (
        r"function\s+handleRemoteCameraUpdate\(data\)\s*\{\s*"
        r"//\s*Only sync camera if this window is idle\s*"
        r"if \(isWindowActive\) return;"
    )
    assert re.search(pattern, HTML_SOURCE, flags=re.DOTALL)


def test_focus_blur_gates_midi_input() -> None:
    focus_handler = r"window\.addEventListener\('focus',\s*\(\) => \{[^}]*isWindowActive = true;[^}]*updateMultiWindowStatus\(\);"
    blur_handler = r"window\.addEventListener\('blur',\s*\(\) => \{[^}]*isWindowActive = false;[^}]*updateMultiWindowStatus\(\);"
    visibility_handler = r"document\.addEventListener\('visibilitychange',\s*\(\) => \{[^}]*isWindowActive = !document\.hidden;"
    assert re.search(focus_handler, HTML_SOURCE, flags=re.DOTALL)
    assert re.search(blur_handler, HTML_SOURCE, flags=re.DOTALL)
    assert re.search(visibility_handler, HTML_SOURCE, flags=re.DOTALL)


def test_multiwindow_hud_indicator_states() -> None:
    status_pattern = r"const activeText = isWindowActive \? 'Active' : 'Idle';\s*status\.textContent = `Multi-Window: \${activeText}"
    color_pattern = r"status\.style\.color = isWindowActive \? '#10b981' : '#f59e0b';"
    assert re.search(status_pattern, HTML_SOURCE, flags=re.DOTALL)
    assert re.search(color_pattern, HTML_SOURCE, flags=re.DOTALL)
    assert "multiwindow-status" in HTML_SOURCE
