import pytest
import numpy as np
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.services.catalog_service import catalog_service
from backend.app.services.trace_service import trace_service
from backend.app.tools.fusion_tool import OpticalSARFusionTool
from backend.app.tools.vqa_tool import RSVqaTool

client = TestClient(app)


def test_catalog_service_scenes():
    scenes = catalog_service.get_all_scenes()
    assert len(scenes) >= 4
    # Check that each scene has required metadata
    for s in scenes:
        assert "scene_id" in s
        assert "sensor" in s
        assert "resolution_m" in s
        assert "crs" in s


def test_catalog_filter_by_aoi():
    vizag_scenes = catalog_service.filter_scenes(aoi="Visakhapatnam")
    assert len(vizag_scenes) >= 1
    assert any("Visakhapatnam" in s["aoi"] for s in vizag_scenes)


def test_catalog_todays_scenario():
    today_sc = catalog_service.get_todays_scenario()
    assert today_sc.id == "scenario_today_near_real_time"
    assert "Today" in today_sc.title or "Operational" in today_sc.title
    assert len(today_sc.image_paths) >= 1


def test_trace_service_persistence():
    test_trace_id = "trace-test-integrity-12345"
    sample_trace = {
        "trace_id": test_trace_id,
        "task_type": "optical_sar_fusion",
        "total_execution_time_ms": 42.5,
        "tools_executed": [{"tool_name": "Optical_SAR_Fusion_Specialist_v1"}]
    }
    saved_path = trace_service.save_trace(test_trace_id, sample_trace)
    assert saved_path is not None
    
    retrieved = trace_service.get_trace(test_trace_id)
    assert retrieved is not None
    assert retrieved["trace_id"] == test_trace_id
    assert "integrity_hash" in retrieved


def test_sar_backscatter_physics():
    fusion_tool = OpticalSARFusionTool()
    # Create high-amplitude test image (representing metal tank corner double-bounce)
    opt = np.ones((100, 100, 3), dtype=np.uint8) * 230
    sar = np.ones((100, 100, 3), dtype=np.uint8) * 250  # ~0 dB
    
    res = fusion_tool.run([opt, sar], query="penetrate cloud cover")
    assert res.confidence >= 0.90
    assert "mean_sigma0_db" in res.parameters
    assert res.parameters["double_bounce_thresh_db"] == -9.0
    assert res.parameters["specular_thresh_db"] == -21.0


def test_api_scenes_endpoint():
    resp = client.get("/api/v1/scenes")
    assert resp.status_code == 200
    scenes = resp.json()
    assert isinstance(scenes, list)
    assert len(scenes) >= 4


def test_api_scenarios_today_endpoint():
    resp = client.get("/api/v1/scenarios/today")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "scenario_today_near_real_time"


def test_api_traces_endpoint():
    resp = client.get("/api/v1/traces")
    assert resp.status_code == 200
    traces = resp.json()
    assert isinstance(traces, list)


def test_analyze_scenario_4_coastal():
    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "What new coastal infrastructure or breakwater structures were constructed between T1 and T2?",
            "scenario_id": "scenario_4_coastal"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["detected_task"] == "change_detection"
    assert data["result"]["confidence_score"] >= 0.85
    assert data["result"]["visual_evidence"]["overlay_base64"] is not None
