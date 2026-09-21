import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_get_demo_packages_endpoint():
    response = client.get("/api/demo-packages")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] >= 3
    
    pkg_ids = [p["id"] for p in data["packages"]]
    assert "gudlavalleru_urban_growth" in pkg_ids
    assert "machilipatnam_coastal_change" in pkg_ids
    assert "godavari_basin_flood" in pkg_ids

    # Verify Gudlavalleru package metrics
    gvl = next(p for p in data["packages"] if p["id"] == "gudlavalleru_urban_growth")
    assert gvl["statistics"]["changed_area_ha"] > 0
    assert gvl["statistics"]["classes"]["new_builtup_ha"] > 0
    assert gvl["quality"]["valid_pixel_percentage"] == 100.0
    assert gvl["statistics"]["confidence_score"] > 0.8


def test_scenarios_lists_verified_packages():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    ids = [s["id"] for s in data]
    assert "gudlavalleru_urban_growth" in ids
    assert "machilipatnam_coastal_change" in ids
    assert "godavari_basin_flood" in ids


def test_analyze_gudlavalleru_urban_growth():
    response = client.post(
        "/api/v1/analyze",
        data={
            "query": "What changed between 2025 and 2026 in Gudlavalleru?",
            "scenario_id": "gudlavalleru_urban_growth",
            "task_hint": "change_detection"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["detected_task"] == "change_detection"
    
    # Check visual evidence
    vis = data["result"]["visual_evidence"]
    assert vis is not None
    assert vis["overlay_base64"] is not None
    assert vis["overlay_base64"].startswith("data:image/png;base64,")
    
    # Check metric summary
    metrics = vis["metric_summary"]
    assert metrics["area_hectares"] > 100.0  # ~242.1 ha
    assert metrics["builtup_expansion_hectares"] > 100.0
    
    # Check confidence is dynamic and honest
    assert data["result"]["confidence_score"] > 0.80
    assert "242.1" in data["result"]["text_answer"] or "hectares" in data["result"]["text_answer"]


def test_analyze_machilipatnam_coastal_change():
    response = client.post(
        "/api/v1/analyze",
        data={
            "query": "What new coastal infrastructure or breakwater structures were constructed?",
            "scenario_id": "machilipatnam_coastal_change",
            "task_hint": "change_detection"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    vis = data["result"]["visual_evidence"]
    assert vis["metric_summary"]["area_hectares"] > 50.0  # ~158.3 ha


def test_analyze_godavari_basin_flood():
    response = client.post(
        "/api/v1/analyze",
        data={
            "query": "Identify the submerged agricultural parcels and quantify flood inundation area in hectares.",
            "scenario_id": "godavari_basin_flood",
            "task_hint": "change_detection"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    vis = data["result"]["visual_evidence"]
    assert vis["metric_summary"]["area_hectares"] > 300.0  # ~627.5 ha
    assert vis["metric_summary"]["water_increase_hectares"] > 300.0
