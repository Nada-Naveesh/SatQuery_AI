import pytest
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.services.catalog_service import catalog_service

client = TestClient(app)


def test_analyze_nrt_scenario_no_unbound_local_error():
    """
    CRITICAL BUG FIX VERIFICATION:
    Tests that POST /api/v1/analyze with scenario_today_near_real_time does not raise
    UnboundLocalError for 's_dir' and returns a valid 200 AnalysisResponse.
    """
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Provide operational surveillance report on today's satellite acquisition.",
            "scenario_id": "scenario_today_near_real_time",
            "task_hint": "auto"
        }
    )
    assert resp.status_code == 200, f"Failed with: {resp.text}"
    data = resp.json()
    assert "result" in data
    assert "execution_trace" in data
    assert data["result"]["confidence_score"] > 0.5


def test_api_scenes_gudlavalleru_catalog_filtering():
    """
    Tests GET /api/scenes?aoi=gudlavalleru&sensor=sentinel-2&date_from=2025-01-01&date_to=2026-12-31.
    Verifies response shape { "scenes": [ ... ] } with Gudlavalleru scenes.
    """
    resp = client.get(
        "/api/scenes",
        params={
            "aoi": "gudlavalleru",
            "sensor": "sentinel-2",
            "date_from": "2025-01-01",
            "date_to": "2026-12-31"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "scenes" in data
    scenes = data["scenes"]
    assert len(scenes) >= 2
    
    ids = [s["id"] for s in scenes]
    assert "gvl_s2_2025_09_03" in ids
    assert "gvl_s2_2026_09_05" in ids

    # Check required fields
    for s in scenes:
        assert "id" in s
        assert "aoi" in s
        assert "sensor" in s
        assert "level" in s
        assert "date" in s
        assert "cloud_cover" in s
        assert "thumbnail_url" in s
        assert "metadata_url" in s


def test_api_scenes_detail_metadata():
    """
    Tests GET /api/scenes/{scene_id} returns full metadata for Gudlavalleru scene.
    """
    resp = client.get("/api/scenes/gvl_s2_2025_09_03")
    assert resp.status_code == 200
    scene = resp.json()
    assert scene["id"] == "gvl_s2_2025_09_03"
    assert scene["aoi"] == "gudlavalleru"
    assert scene["sensor"] == "Sentinel-2"
    assert "bands" in scene
    assert "resolution_m" in scene
    assert "path_rgb" in scene


def test_analyze_gudlavalleru_single_scene():
    """
    Tests single-scene analysis on Gudlavalleru 2025 scene.
    """
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Highlight agricultural fields and identify water channels.",
            "scene_ids": "gvl_s2_2025_09_03",
            "analysis_mode": "single"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["confidence_score"] > 0.5
    assert "visual_evidence" in data["result"]


def test_analyze_gudlavalleru_bitemporal_change():
    """
    Tests bi-temporal change detection comparing Gudlavalleru 2025 vs 2026.
    """
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "What changed between 2025 and 2026 in this area?",
            "scene_ids": "gvl_s2_2025_09_03,gvl_s2_2026_09_05",
            "analysis_mode": "change"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_task"] in ("bi_temporal_change_detection", "change_detection")
    assert data["result"]["visual_evidence"] is not None
    assert data["result"]["visual_evidence"]["metric_summary"] is not None


def test_api_analyze_alias_endpoint():
    """
    Tests POST /api/analyze route alias with Gudlavalleru scenes.
    """
    resp = client.post(
        "/api/analyze",
        data={
            "query": "Quantify urban infrastructure change between 2025 and 2026.",
            "scene_ids": "gvl_s2_2025_09_03,gvl_s2_2026_09_05",
            "analysis_mode": "change"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["confidence_score"] > 0.6


def test_analyze_invalid_scene_404():
    """
    Verifies that a nonexistent scene ID returns a 404 with a helpful message.
    """
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Test query",
            "scene_ids": "nonexistent_scene_xyz"
        }
    )
    assert resp.status_code == 404
