from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / "microfiche" / "index.html").read_text(encoding="utf-8")


def test_progressive_loading_uses_visible_batch_and_placeholders():
    assert "visibleBatchSize" in HTML
    assert "const useStreaming = config.streaming.enabled && totalItems > config.streaming.smallCollectionThreshold" in HTML
    assert "placeholder sprites" in HTML or "placeholderSprites" in HTML


def test_prefetch_queue_populates_and_processes():
    assert "function updatePrefetching()" in HTML
    assert "function predictAndPrefetch()" in HTML
    assert "function processPrefetchQueue()" in HTML
    assert "streamingManager.prefetchQueue = prefetchIndices" in HTML


def test_pagination_chunk_loader_tracks_requests():
    assert "async function loadMediaChunk" in HTML
    assert "streamingManager.loadingChunks.add(chunkId);" in HTML
    assert "streamingManager.loadedChunks" in HTML
    assert "fetch(`${config.encoder_base}/collection/${config.collection_id}?start=${startIndex}&count=${count}`" in HTML


def test_offline_mode_uses_cache_and_updates_hud():
    assert 'id="offline-badge"' in HTML
    assert "updateStreamingStatus('Loading', !streamingManager.isOnline, true);" in HTML
    assert "getCachedCollection(config.collection_id)" in HTML
    assert "cacheCollection(config.collection_id" in HTML


def test_small_collection_falls_back_to_legacy_behavior():
    assert "const useStreaming =" in HTML
    assert "Small collection" in HTML
    assert "streamingManager.enabled = useStreaming" in HTML


def test_streaming_does_not_modify_collaborative_payloads():
    assert "sendCollaborativeMessage('parameter_change', {\n        parameter: 'spectral_fft_size'" in HTML or "sendCollaborativeMessage('parameter_change', {" in HTML
    assert "sendCollaborativeMessage('panel_change'" in HTML
    assert "sendCollaborativeMessage('streaming'" not in HTML
