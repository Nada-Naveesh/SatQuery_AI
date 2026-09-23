"""
SatQuery AI - State-Wide Andhra Pradesh Coverage & Analysis Tests
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)

Verifies full coverage across all Andhra Pradesh major cities and regions:
- Vijayawada, Amaravati, Visakhapatnam, Tirupati, Guntur, Rajahmundry,
  Kakinada, Kurnool, Nellore, Anantapur, AP State Overview, and Gudlavalleru.
- Verifies catalog discovery, scene metadata, and multi-temporal change detection.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.catalog_service import catalog_service

client = TestClient(app)


def test_ap_coverage_catalog_contains_all_major_cities():
    """
    Verifies that catalog indexes Sentinel-2 scenes for all key Andhra Pradesh regions.
    """
    key_ap_regions = [
        "vijayawada",
        "amaravati",
        "visakhapatnam",
        "tirupati",
        "guntur",
        "rajahmundry",
        "kakinada",
        "kurnool",
        "nellore",
        "anantapur",
        "gudlavalleru",
    ]

    for region in key_ap_regions:
        resp = client.get(f"/api/scenes?aoi={region}")
        assert resp.status_code == 200, f"Failed querying scenes for {region}"
        data = resp.json()
        assert "scenes" in data
        assert len(data["scenes"]) >= 2, f"Expected at least 2 scenes (2025 & 2026) for {region}, got {len(data['scenes'])}"
        
        # Verify both 2025 and 2026 years exist
        years = [s["date"][:4] for s in data["scenes"]]
        assert "2025" in years, f"Missing 2025 scene for {region}"
        assert "2026" in years, f"Missing 2026 scene for {region}"


def test_vijayawada_scene_metadata():
    """
    Verifies detailed scene metadata for Vijayawada.
    """
    resp = client.get("/api/scenes?aoi=vijayawada")
    assert resp.status_code == 200
    scenes = resp.json()["scenes"]
    vja_2026 = next(s for s in scenes if "2026" in s["date"])
    
    # Query full scene detail
    detail_resp = client.get(f"/api/scenes/{vja_2026['id']}")
    assert detail_resp.status_code == 200
    meta = detail_resp.json()
    assert "Vijayawada" in meta["aoi"]
    assert meta["coordinates"][0] == pytest.approx(16.51, abs=0.05)
    assert meta["coordinates"][1] == pytest.approx(80.65, abs=0.05)
    assert meta["resolution_m"] == 10.0
    assert "B02" in meta["bands"]
    assert "B08" in meta["bands"]


def test_amaravati_scene_metadata():
    """
    Verifies detailed scene metadata for Amaravati Capital Region.
    """
    resp = client.get("/api/scenes?aoi=amaravati")
    assert resp.status_code == 200
    scenes = resp.json()["scenes"]
    assert len(scenes) >= 2
    amr_meta = client.get(f"/api/scenes/{scenes[0]['id']}").json()
    assert "Amaravati" in amr_meta["aoi"]
    assert amr_meta["coordinates"][0] == pytest.approx(16.54, abs=0.05)
    assert amr_meta["coordinates"][1] == pytest.approx(80.51, abs=0.05)


def test_analyze_vijayawada_bitemporal_change():
    """
    Executes bi-temporal change detection comparing Vijayawada 2025 vs 2026.
    Ensures that agentic analysis processes the actual Vijayawada Sentinel-2 scenes.
    """
    vja_scenes = catalog_service.filter_scenes(aoi="vijayawada")
    assert len(vja_scenes) >= 2
    s1, s2 = vja_scenes[0]["id"], vja_scenes[1]["id"]

    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "What infrastructure and hydrological changes occurred in Vijayawada between 2025 and 2026?",
            "scene_ids": f"{s1},{s2}",
            "analysis_mode": "change"
        }
    )
    assert resp.status_code == 200, f"Analysis failed: {resp.text}"
    data = resp.json()
    assert data["detected_task"] in ("bi_temporal_change_detection", "change_detection")
    assert data["result"]["confidence_score"] > 0.5
    assert "visual_evidence" in data["result"]
    assert data["result"]["visual_evidence"]["overlay_base64"] is not None
    assert "Vijayawada" in data["input_summary"]["area"]


def test_analyze_kurnool_solar_park_scene():
    """
    Executes single-scene analysis on Kurnool solar park scene.
    """
    knl_scenes = catalog_service.filter_scenes(aoi="kurnool")
    assert len(knl_scenes) >= 1
    s_id = knl_scenes[0]["id"]

    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Inspect solar park arrays and land surface conditions.",
            "scene_ids": s_id,
            "analysis_mode": "single"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["confidence_score"] > 0.5
    assert data["input_summary"]["sensor"] == "Sentinel-2"


def test_mission_control_html_serves_ap_coverage():
    """
    Verifies that the root Mission Control HTML dashboard supports arbitrary search and includes key regions.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "Vijayawada" in html
    assert "Amaravati" in html
    assert "Visakhapatnam" in html
    assert "Tirupati" in html
    assert "Kurnool" in html
    assert "Avanigadda" in html
    assert "viewerCoordsOverlay" in html
    assert "hudLatLon" in html
    assert "sceneCoordinatesBadge" in html
    assert "dataGuideModal" in html
    assert "How to Get Free Satellite Images" in html


def test_aoi_search_endpoint():
    """
    Verifies the GET /api/aoi/search endpoint returns structured geographic data.
    """
    # Test Vijayawada
    resp = client.get("/api/aoi/search?q=Vijayawada")
    assert resp.status_code == 200
    data = resp.json()
    assert data["aoi"] == "vijayawada"
    assert "Vijayawada" in data["display_name"]
    assert data["center"]["lat"] == pytest.approx(16.51, abs=0.05)
    assert data["center"]["lon"] == pytest.approx(80.65, abs=0.05)

    # Test Gudlavalleru
    resp_gvl = client.get("/api/aoi/search?q=Gudlavalleru")
    assert resp_gvl.status_code == 200
    data_gvl = resp_gvl.json()
    assert data_gvl["aoi"] == "gudlavalleru"
    assert data_gvl["center"]["lat"] == pytest.approx(16.02, abs=0.05)

    # Test Tirupati
    resp_tpt = client.get("/api/v1/aoi/search?q=Tirupati")
    assert resp_tpt.status_code == 200
    assert resp_tpt.json()["aoi"] == "tirupati"


def test_how_to_use_guide_ribbon_in_html():
    """
    Verifies that the Quick Start Guide ribbon and toggle functions exist in Mission Control HTML.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text
    assert "howToUseGuide" in html
    assert "Quick Start Guide" in html
    assert "toggleHowToUseGuide" in html
    assert "Select Location" in html
    assert "Discover Scenes" in html
    assert "Load Both Scenes" in html
    assert "Detect &amp; Quantify" in html


def test_all_cities_bitemporal_change_nonzero_hectares():
    """
    Verifies that all 8 key Andhra Pradesh cities produce non-zero physical hectares
    for both New Built-up and Vegetation Loss, resolving the 0.0 ha issue completely.
    """
    cities = [
        "vijayawada",
        "amaravati",
        "visakhapatnam",
        "tirupati",
        "kurnool",
        "gudlavalleru",
        "avanigadda",
        "kankipadu",
    ]

    for city in cities:
        s1 = f"copernicus_{city}_s2_2025"
        s2 = f"copernicus_{city}_s2_2026"
        resp = client.post(
            "/api/v1/analyze",
            data={
                "query": f"Detect urban expansion and vegetation changes in {city}.",
                "scene_ids": f"{s1},{s2}",
                "analysis_mode": "change"
            }
        )
        assert resp.status_code == 200, f"Analysis failed for {city}: {resp.text}"
        data = resp.json()
        metric = data.get("result", {}).get("visual_evidence", {}).get("metric_summary", {})
        total_ha = metric.get("area_hectares", 0.0)
        builtup_ha = metric.get("builtup_expansion_hectares", 0.0)
        vegloss_ha = metric.get("vegetation_loss_hectares", 0.0)
        water_ha = metric.get("water_increase_hectares", 0.0)

        assert total_ha > 0.0, f"{city} total_ha must be > 0"
        assert builtup_ha > 0.0, f"{city} built_up_increase_ha must be > 0, got {builtup_ha}"
        assert vegloss_ha > 0.0, f"{city} vegetation_loss_ha must be > 0, got {vegloss_ha}"
        assert water_ha > 0.0, f"{city} water_changes_ha must be > 0, got {water_ha}"

