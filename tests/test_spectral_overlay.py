import re
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")


def test_fft_overlay_draggable_and_resizable():
    assert "header.addEventListener('mousedown'" in HTML
    assert "Math.max(0, Math.min(maxX, newX))" in HTML
    assert "ResizeObserver" in HTML and "resizeFFTCanvas();" in HTML


def test_fft_presets_keep_slider_in_sync():
    assert "updateFFTSize(newSize, true)" in HTML
    assert "fftSizeSlider.value = fftSize;" in HTML
    assert "presetBtns.forEach" in HTML and "btn.dataset.size" in HTML


def test_fft_log_scale_affects_rendering():
    assert "logFrequencyScale = !logFrequencyScale" in HTML
    assert "const dataIndex = logFrequencyScale ? getLogIndex" in HTML
    assert "processedLine = new Array" in HTML and "getLogIndex" in HTML


def test_fft_collaborative_toasts_and_payloads():
    assert "sendCollaborativeMessage('parameter_change', {\n        parameter: 'spectral_enabled'" in HTML
    for param in ('spectral_mode', 'spectral_fft_size', 'spectral_log_scale'):
        assert f"parameter: '{param}'" in HTML
    assert "function showCollaborativeSpectralToast" in HTML
    assert "showSpectralToast(`Log frequency" in HTML


def test_fft_bar_and_waterfall_renderers_exist():
    assert "function renderFFTBars" in HTML
    assert "function renderFFTWaterfall" in HTML
    assert "spectralMode === 'bars'" in HTML
    assert "spectralMode === 'waterfall'" in HTML
