import re
from pathlib import Path

HTML_SOURCE = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")


def test_fft_window_configuration_and_buffer_size():
    assert "analyser.fftSize = 256" in HTML_SOURCE
    assert "fftDataArray = new Uint8Array(bufferLength);" in HTML_SOURCE


def test_fft_toggle_controls_visibility():
    assert "fftToggle.addEventListener" in HTML_SOURCE
    assert "stopFFTAnalysis();" in HTML_SOURCE
    assert "fftOverlay.style.display = 'none';" in HTML_SOURCE
    assert "document.getElementById('fft-overlay').style.display = 'flex';" in HTML_SOURCE


def test_fft_renders_bars_and_waterfall():
    assert "fftCanvasContext.fillRect" in HTML_SOURCE  # bar rendering
    assert "putImageData(imageData, 0, 1);" in HTML_SOURCE  # waterfall trail


def test_collaboration_and_midi_flows_intact():
    for signature in (
        "sendCollaborativeMessage('sprite_interaction'",
        "sendCollaborativeMessage('parameter_change'",
        "sendCollaborativeMessage('chat_message'",
        "sendCollaborativeMessage('preset_applied'",
        "connectMidiWebSocket();",
    ):
        assert signature in HTML_SOURCE
