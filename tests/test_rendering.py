from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")


def test_lod_switches_for_large_collections():
    assert "const useLOD = lodConfig.enabled && mediaCount >= lodConfig.smallCollectionThreshold;" in HTML
    assert "lodStats = { high: sprites.length, medium: 0, low: 0 }" in HTML
    assert "const lodLevel = getLODLevel" in HTML


def test_lod_disabled_for_small_collections():
    assert "smallCollectionThreshold: 200" in HTML
    assert "if (!lodConfig.enabled) {" in HTML
    assert "sprite.userData.lodLevel = 'high';" in HTML


def test_instanced_rendering_path_present():
    assert "const useInstancedRendering = mediaCount >= lodConfig.instancedRenderingThreshold;" in HTML
    assert "if (useInstancedRendering) {" in HTML
    assert "createInstancedSprites(collection.media, outerRadius);" in HTML


def test_fps_monitor_updates_hud():
    assert "fpsMonitor.frameCount++" in HTML
    assert "fpsMonitor.fps = Math.round" in HTML
    assert "fpsValue.textContent = fpsMonitor.fps;" in HTML


def test_lod_toggle_updates_config_and_hud():
    assert "const lodToggle = document.getElementById('lod-toggle');" in HTML
    assert "lodToggle.addEventListener('change'" in HTML
    assert "lodConfig.enabled = e.target.checked;" in HTML
    assert "updatePerformanceHUD();" in HTML


def test_lod_mode_default_behaviour_for_small_collections():
    assert "performanceStats.spriteCount = mediaCount;" in HTML
    assert "if (lodStats && lodConfig.enabled && performanceStats.spriteCount >= lodConfig.smallCollectionThreshold)" in HTML
    assert "lodStats.style.display = 'none';" in HTML
