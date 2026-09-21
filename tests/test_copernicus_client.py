"""
SatQuery AI - Copernicus CDSE Discovery & Session Trace Verification
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)

Tests:
1. Copernicus Sentinel-2 scene discovery (live CDSE & resilient fallback).
2. Auditable execution traces retrieval (GET /api/traces/{trace_id}).
3. Multi-query conversational session chaining with session_trace_id.
4. Calibrated confidence explanation & explainable overlay assertions.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.copernicus_service import copernicus_service

client = TestClient(app)


def test_copernicus_scenes_gudlavalleru():
    """Verifies Copernicus scene discovery for Gudlavalleru."""
    resp = client.get("/api/copernicus/scenes?aoi_name=Gudlavalleru&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert "provider" in data
    assert "scenes" in data
    assert len(data["scenes"]) >= 1
    scene = data["scenes"][0]
    assert "id" in scene
    assert "date" in scene
    assert "cloud_cover" in scene
    assert scene["cloud_cover"] <= 30.0


def test_copernicus_scenes_visakhapatnam_bbox():
    """Verifies scene search with explicit geographic bounding box."""
    resp = client.get("/api/copernicus/scenes?aoi_name=Visakhapatnam&bbox=17.65,83.25,17.75,83.35&limit=3")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scenes"]) >= 1
    assert data["aoi"] == "Visakhapatnam"


def test_copernicus_service_unit():
    """Direct unit test of copernicus_service search_scenes."""
    res = copernicus_service.search_scenes(aoi_name="Amaravati", limit=2)
    assert "scenes" in res
    assert len(res["scenes"]) > 0
    assert "Copernicus" in res["provider"] or "Local" in res["provider"]


def test_trace_retrieval_and_listing():
    """Verifies listing and querying execution traces."""
    # First, run an analysis to generate a fresh trace
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Identify flood extents and waterlogged regions in the Godavari basin.",
            "scenario_id": "scenario_1_flood",
            "task_hint": "flood_water_index"
        }
    )
    assert resp.status_code == 200
    res_data = resp.json()
    trace_id = res_data["execution_trace"]["trace_id"]
    assert trace_id is not None

    # Check confidence_explanation exists
    assert "confidence_explanation" in res_data["result"]
    assert res_data["result"]["confidence_explanation"] is not None
    assert len(res_data["result"]["confidence_explanation"]) > 10

    # Retrieve specific trace
    trace_resp = client.get(f"/api/traces/{trace_id}")
    assert trace_resp.status_code == 200
    trace_data = trace_resp.json()
    assert trace_data["trace_id"] == trace_id
    assert "tools_executed" in trace_data or "analysis_result" in trace_data

    # Retrieve trace listing
    list_resp = client.get("/api/traces")
    assert list_resp.status_code == 200
    traces = list_resp.json()
    assert isinstance(traces, list)
    assert any(t["trace_id"] == trace_id for t in traces)


def test_trace_not_found():
    """Verifies 404 response for invalid trace IDs."""
    resp = client.get("/api/traces/non_existent_trace_id_9999")
    assert resp.status_code == 404


def test_multi_query_session_chaining():
    """
    Verifies that session_trace_id can be used to ask follow-up questions
    without needing to upload new imagery.
    """
    # Step 1: Initial query
    resp1 = client.post(
        "/api/v1/analyze",
        data={
            "query": "What are the primary surface water changes?",
            "scenario_id": "scenario_1_flood",
            "task_hint": "flood_water_index"
        }
    )
    assert resp1.status_code == 200
    trace_id_1 = resp1.json()["execution_trace"]["trace_id"]

    # Step 2: Follow-up query reusing session_trace_id
    resp2 = client.post(
        "/api/v1/analyze",
        data={
            "query": "Can you summarize agricultural damage and recovery potential?",
            "session_trace_id": trace_id_1,
            "task_hint": "auto"
        }
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["result"]["confidence_score"] > 0.5
    assert data2["execution_trace"]["trace_id"] != trace_id_1


def test_copernicus_scene_analyze_single_and_bitemporal():
    """
    Verifies that scenes discovered via Copernicus search can be immediately analyzed
    in both single-scene VQA and bi-temporal change detection modes without 404 errors.
    """
    # 1. Discover scenes for arbitrary place (e.g. Delhi)
    search_resp = client.get("/api/copernicus/scenes?aoi_name=Delhi&limit=2")
    assert search_resp.status_code == 200
    scenes = search_resp.json()["scenes"]
    assert len(scenes) >= 2
    sid1 = scenes[0]["id"]
    sid2 = scenes[1]["id"]

    # 2. Single scene analyze
    resp_single = client.post(
        "/api/v1/analyze",
        data={
            "query": "Analyze infrastructure and land cover in Delhi.",
            "scene_ids": sid1,
            "analysis_mode": "single"
        }
    )
    assert resp_single.status_code == 200
    data_single = resp_single.json()
    assert data_single["status"] == "success"
    assert data_single["result"]["confidence_score"] > 0.5
    assert "visual_evidence" in data_single["result"]

    # 3. Bi-temporal change analyze
    resp_change = client.post(
        "/api/v1/analyze",
        data={
            "query": "What changed in Delhi between 2025 and 2026?",
            "scene_ids": f"{sid1},{sid2}",
            "analysis_mode": "change"
        }
    )
    assert resp_change.status_code == 200
    data_change = resp_change.json()
    assert data_change["status"] == "success"
    assert data_change["detected_task"] in ("change_detection", "bi_temporal_change_detection")
    assert data_change["result"]["confidence_score"] > 0.5
    assert data_change["result"]["visual_evidence"]["overlay_base64"] is not None

