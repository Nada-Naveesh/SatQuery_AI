"""
SatQuery AI - Live Location Analysis & Asynchronous Job Lifecycle Verification
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)

Tests:
1. Location search endpoint (/api/location/search) with place names and coordinate pairs.
2. Copernicus scene discovery with coordinates and bounding boxes.
3. Asynchronous analysis lifecycle: /api/analysis/start -> /api/analysis/{job_id} -> results & overlay.
4. Physical area calculation with georeferenced and non-georeferenced images (0.0 ha prevention).
"""

import time
import pytest
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.services.location_service import location_service
from backend.app.processing.area_stats import calculate_physical_area_statistics
from backend.app.processing.change_detection import ChangeClassificationResult, CLASS_NEW_BUILTUP, CLASS_VEG_DECREASE
import numpy as np

client = TestClient(app)


def test_location_search_place_names():
    """Tests geocoding of various Indian locations via location search."""
    # 1. Gudlavalleru
    res = client.get("/api/location/search?q=Gudlavalleru")
    assert res.status_code == 200
    data = res.json()
    assert "gudlavalleru" in data["name"].lower()
    assert len(data["bbox"]) == 4
    assert 15.0 < data["lat"] < 17.0
    assert 80.0 < data["lon"] < 82.0
    assert "coordinates_display" in data

    # 2. Avanigadda
    res2 = client.get("/api/location/search?q=Avanigadda")
    assert res2.status_code == 200
    data2 = res2.json()
    assert "avanigadda" in data2["name"].lower()
    assert 15.0 < data2["lat"] < 17.0


def test_location_search_coordinates():
    """Tests geocoding from direct numeric coordinate strings."""
    res = client.get("/api/location/search?q=16.5100,80.6500")
    assert res.status_code == 200
    data = res.json()
    assert abs(data["lat"] - 16.51) < 0.01
    assert abs(data["lon"] - 80.65) < 0.01
    assert len(data["bbox"]) == 4


def test_copernicus_scenes_with_location():
    """Tests fetching scenes for a place via the live API."""
    res = client.get("/api/copernicus/scenes?aoi_name=Vijayawada&limit=3")
    assert res.status_code == 200
    data = res.json()
    assert "scenes" in data
    assert len(data["scenes"]) >= 1
    sc = data["scenes"][0]
    assert "id" in sc
    assert "date" in sc
    assert "cloud_cover" in sc


def test_async_analysis_job_lifecycle():
    """Tests launching an asynchronous analysis job, polling progress, and retrieving results."""
    # 1. Start job
    start_res = client.post(
        "/api/analysis/start",
        data={
            "query": "Quantify changes in land use and measure differences in hectares",
            "location_name": "Gudlavalleru",
            "scene_id_1": "gvl_s2_2025_09_03",
            "scene_id_2": "gvl_s2_2026_09_05"
        }
    )
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert "job_id" in start_data
    job_id = start_data["job_id"]
    assert start_data["status"] in ["pending", "running", "completed"]

    # 2. Poll for completion (max 15 iterations, 0.2s each)
    completed = False
    for _ in range(15):
        poll_res = client.get(f"/api/analysis/{job_id}")
        assert poll_res.status_code == 200
        job_data = poll_res.json()
        if job_data["status"] == "completed":
            completed = True
            break
        elif job_data["status"] == "failed":
            pytest.fail(f"Analysis job failed: {job_data.get('error_message')}")
        time.sleep(0.2)

    assert completed, f"Job {job_id} did not finish within timeout"

    # 3. Retrieve results
    res_endpoint = client.get(f"/api/analysis/{job_id}/results")
    assert res_endpoint.status_code == 200
    res_data = res_endpoint.json()
    assert res_data["status"] == "success"
    assert "areas" in res_data
    assert "direct_answer" in res_data
    assert "visual_evidence" in res_data
    assert res_data["areas"]["is_georeferenced"] is True
    assert res_data["areas"]["total_changed_ha"] >= 0

    # 4. Retrieve overlay
    overlay_res = client.get(f"/api/analysis/{job_id}/overlay")
    assert overlay_res.status_code == 200
    assert overlay_res.headers["content-type"] == "image/png"
    assert len(overlay_res.content) > 100


def test_physical_area_calculation_georeferenced_vs_unreferenced():
    """Verifies area_stats.py produces accurate metrics and handles unreferenced images honestly."""
    # Mock change detection result with known pixel counts
    # 512x512 = 262144 pixels. 2500 pixels built-up, 900 veg loss
    h, w = 512, 512
    change_mask = np.zeros((h, w), dtype=np.uint8)
    change_mask[50:100, 50:100] = CLASS_NEW_BUILTUP   # 2500 pixels
    change_mask[120:150, 120:150] = CLASS_VEG_DECREASE  # 900 pixels

    mock_cd = ChangeClassificationResult(
        classified_mask=change_mask,
        delta_ndvi=np.zeros((h, w), dtype=np.float32),
        delta_ndwi=np.zeros((h, w), dtype=np.float32),
        delta_builtup=np.zeros((h, w), dtype=np.float32),
        spectral_diff=np.zeros((h, w), dtype=np.float32),
        builtup_mask=(change_mask == CLASS_NEW_BUILTUP),
        veg_increase_mask=np.zeros((h, w), dtype=bool),
        veg_decrease_mask=(change_mask == CLASS_VEG_DECREASE),
        water_increase_mask=np.zeros((h, w), dtype=bool),
        water_decrease_mask=np.zeros((h, w), dtype=bool),
        cloud_mask=np.zeros((h, w), dtype=bool)
    )

    # 1. Georeferenced (10m Sentinel-2 pixel = 0.01 ha)
    # 3400 pixels * 0.01 ha = 34.0 ha
    stats_geo = calculate_physical_area_statistics(
        change_result=mock_cd,
        resolution_m=10.0,
        crs="EPSG:4326",
        is_georeferenced=True,
        date1="2025-09-03",
        date2="2026-09-05",
        location_name="Gudlavalleru"
    )
    assert stats_geo.is_georeferenced is True
    assert abs(stats_geo.changed_area_ha - 34.0) < 0.1
    assert abs(stats_geo.builtup_ha - 25.0) < 0.1
    assert abs(stats_geo.veg_dec_ha - 9.0) < 0.1
    assert stats_geo.limitation_notice is None
    assert "34.00 ha" in stats_geo.total_changed_display

    # 2. Non-georeferenced PNG/JPG upload
    stats_unref = calculate_physical_area_statistics(
        change_result=mock_cd,
        resolution_m=10.0,
        crs="EPSG:4326",
        is_georeferenced=False,
        date1="T1",
        date2="T2",
        location_name="Custom Upload"
    )
    assert stats_unref.is_georeferenced is False
    assert "Physical area in hectares is unavailable" in stats_unref.limitation_notice
    assert "geographic coordinate scale" in stats_unref.limitation_notice
