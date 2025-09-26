from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "index_latest.html").read_text(encoding="utf-8")


def test_modal_energy_visualization_and_hud_toggle():
    assert "function renderModalEnergy" in HTML
    assert "modalEnergyHistory.push" in HTML
    assert "const modeColors" in HTML
    assert "spectralHudExpanded =" in HTML
    assert "hudToggleBtn = document.getElementById('spectral-hud-toggle')" in HTML or "hudToggle" in HTML
    assert "advancedControls.style.display = spectralHudExpanded" in HTML


def test_temporal_history_buffer_updates():
    assert "function renderTemporalEvolution" in HTML
    assert "temporalBuffer.push" in HTML
    assert "temporalBuffer.shift" in HTML
    assert "const maxBufferSize" in HTML
    assert "const imageData = ctx.createImageData" in HTML


def test_hud_toggle_button_exists():
    assert 'id="spectral-hud-toggle"' in HTML
    assert "spectralHudExpanded = !spectralHudExpanded" in HTML
    assert "advancedControls = document.getElementById('spectral-advanced-controls')" in HTML


def test_collaborative_spectral_payloads_present():
    for param in (
        "spectral_enabled",
        "spectral_mode",
        "spectral_fft_size",
        "spectral_log_scale",
        "spectral_hud_expanded",
        "spectral_history_depth",
    ):
        assert f"parameter: '{param}'" in HTML
    assert "showCollaborativeSpectralToast" in HTML


def test_backward_compatibility_classic_renderers():
    assert "function renderFFTBars" in HTML
    assert "function renderFFTWaterfall" in HTML
