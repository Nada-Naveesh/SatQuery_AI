import io
import pytest
from starlette.testclient import TestClient
from PIL import Image

from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["ps_id"] == "26167"
    assert len(data["registered_tools"]) >= 4

def test_scenarios_endpoint():
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 4
    ids = [s["id"] for s in scenarios]
    assert "scenario_1_flood" in ids
    assert "scenario_2_urban" in ids
    assert "scenario_3_optical_sar" in ids
    assert "scenario_4_coastal" in ids

def test_api_scenarios_alias_and_detail():
    # Test /api/scenarios alias
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    assert len(res.json()) >= 4

    # Test /api/scenarios/{id}
    res_detail = client.get("/api/scenarios/scenario_1_flood")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert "Sentinel-2" in detail["sensor"]
    assert detail["area"] is not None
    assert detail["crs"] == "EPSG:4326"
    assert len(detail["suggested_queries"]) >= 1

def test_analyze_scenario_1():
    payload = {
        "query": "Identify the submerged agricultural parcels and highlight their spatial boundaries.",
        "scenario_id": "scenario_1_flood"
    }
    res = client.post("/api/v1/analyze", data=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["detected_task"] in ["visual_question_answering", "region_grounding"]
    assert data["result"]["confidence_score"] > 0.85
    assert data["result"]["visual_evidence"] is not None
    assert "trace-sih-26167-" in data["execution_trace"]["trace_id"]

def test_analyze_scenario_2_temporal():
    payload = {
        "query": "What major infrastructure changes occurred between these two acquisition dates?",
        "scenario_id": "scenario_2_urban"
    }
    res = client.post("/api/v1/analyze", data=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["detected_task"] == "change_detection"
    tool_names = [t["tool_name"] for t in data["execution_trace"]["tools_executed"]]
    assert any("change" in t.lower() or "temporal" in t.lower() for t in tool_names)

def test_analyze_scenario_3_optical_sar():
    payload = {
        "query": "Penetrate cloud cover to map industrial storage tanks and coastal water bodies.",
        "scenario_id": "scenario_3_optical_sar"
    }
    res = client.post("/api/v1/analyze", data=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["detected_task"] == "optical_sar_fusion"
    tool_names = [t["tool_name"] for t in data["execution_trace"]["tools_executed"]]
    assert any("fusion" in t.lower() for t in tool_names)

def test_pdf_report_generation():
    # First analyze to generate trace
    payload = {
        "query": "Identify submerged flood parcels",
        "scenario_id": "scenario_1_flood"
    }
    res = client.post("/api/v1/analyze", data=payload)
    assert res.status_code == 200
    trace_id = res.json()["execution_trace"]["trace_id"]

    # Now request PDF
    pdf_res = client.get(f"/api/v1/report/pdf?trace_id={trace_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 1000  # Non-empty PDF
    assert pdf_res.content.startswith(b"%PDF")
