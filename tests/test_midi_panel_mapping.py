import re
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")


def test_global_mapping_fallback_exists():
    assert "globalMapping = panelMappings.global || {}" in HTML
    assert "panelMappings = { global: globalMapping }" in HTML
    assert "midiMapping = { ...globalMapping }" in HTML


def test_active_panel_mapping_merges_overrides():
    assert "midiMapping = { ...globalMapping, ...panelMappings[panelName] }" in HTML
    assert "setActivePanel(panelName" in HTML


def test_collaborative_messages_include_panel_field():
    assert "sendCollaborativeMessage('panel_change'" in HTML
    assert "panel: activePanel || 'global'" in HTML


def test_panel_control_ui_elements_present():
    assert 'id="spectral-fft-size"' in HTML  # ensure slider exists
    assert 'class="fft-preset-btn" data-size="256"' in HTML
    assert 'id="midi-panel-indicator"' in HTML
    assert 'id="active-panel-name"' in HTML


def test_update_midi_panel_indicator_updates_hud():
    indicator_fn = re.search(r"function updateMidiPanelIndicator\(\)[\s\S]+?}\n", HTML)
    assert indicator_fn is not None
    snippet = indicator_fn.group(0)
    assert "indicator.style.display = 'inline'" in snippet
    assert "panelName.textContent = 'Global'" in snippet


def test_slider_and_presets_sync_calls_update():
    assert "fftSizeSlider.addEventListener('input'" in HTML
    assert "updatePWM" not in HTML  # sanity check unrelated
    assert "updateFFTSize(newSize, true)" in HTML


def test_hud_users_online_badge_present():
    assert 'id="users-online-badge"' in HTML
    badge_fn = re.search(r"function updateUsersOnlineCount\(count\)[\s\S]+?}\n", HTML)
    assert badge_fn is not None
    assert "badge.style.display = 'inline'" in badge_fn.group(0)
    assert "badge.style.display = 'none'" in badge_fn.group(0)
