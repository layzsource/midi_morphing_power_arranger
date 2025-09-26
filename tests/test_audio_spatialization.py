from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "index_latest.html").read_text(encoding="utf-8")


def test_audio_hud_toggle_exists_and_updates_state():
    assert 'id="audio-3d-toggle"' in HTML
    assert "audio3DToggle.addEventListener('click'" in HTML
    assert "audio3DToggle.textContent = spatialAudioEnabled ? 'ON' : 'OFF'" in HTML
    assert "audio3DToggle.className = spatialAudioEnabled ? 'spectral-btn' : 'spectral-btn off'" in HTML


def test_pannernode_creation_and_connections():
    assert "audioContext.createPanner()" in HTML
    assert "panner.positionX.setValueAtTime" in HTML
    assert "audioSources.set(spriteId, { oscillator, gain })" in HTML


def test_position_mapping_from_eigenmodes():
    assert "updateSpriteAudioPositions()" in HTML
    assert "panner.positionZ.setValueAtTime" in HTML
    assert "audioSource.oscillator.frequency.setValueAtTime" in HTML


def test_collaborative_audio_payloads_present():
    for param in (
        "spectral_audio_enabled",
        "spectral_audio_mode",
        "spectral_audio_spread",
        "spectral_audio_position",
    ):
        assert f"parameter: '{param}'" in HTML
    assert "showCollaborativeSpectralToast(data.username, 'spectral_audio_enabled'" in HTML


def test_audio_toast_notifications_use_user_attribution():
    assert "showSpectralToast(`3D Audio ${spatialAudioEnabled ? 'enabled' : 'disabled'}`)" in HTML


def test_audio_fallback_to_stereo_when_unavailable():
    assert "AudioContext not available, falling back to flat stereo" in HTML
    assert "audio3DToggle.textContent = 'UNAVAILABLE'" in HTML


def test_backward_compatibility_renderers_still_present():
    assert "function renderFFTBars" in HTML
    assert "function renderFFTWaterfall" in HTML
