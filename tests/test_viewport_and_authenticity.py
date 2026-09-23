"""
SatQuery AI - Satellite Viewport, Real Imagery, and Authenticity Verification Tests
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)

Verifies:
1. Three core viewport mode controls (Satellite Image, Split Comparison, Evidence View).
2. Clear distinction between Analysis Image (Sentinel-2 L2A) and Reference Basemap (Esri World Imagery).
3. Data authenticity metadata contract (provider, sensor, scene_id, acquisition_date, aoi_bbox [min_lon, min_lat, max_lon, max_lat], resolution_m, analysis_trace_id).
4. Calibrated scientific flood wording for flood/inundation queries.
5. Overlay renderer opacity calibration (40% default alpha).
"""

import pytest
import numpy as np
from starlette.testclient import TestClient

from backend.app.main import app
from backend.app.services.copernicus_service import copernicus_service
from backend.app.processing.overlay_renderer import render_evidence_overlay
from backend.app.processing.change_detection import ChangeClassificationResult, CLASS_WATER_INCREASE, CLASS_UNCHANGED

client = TestClient(app)


def test_mission_control_viewport_mode_buttons_present():
    """
    Verifies that the HTML interface includes the 3 core viewport mode buttons:
    [ Satellite Image ], [ Split Comparison ], and [ Evidence View ].
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert 'id="btnViewSatellite"' in html, "Missing btnViewSatellite button"
    assert 'id="btnViewSplit"' in html, "Missing btnViewSplit button"
    assert 'id="btnViewEvidence"' in html, "Missing btnViewEvidence button"
    assert "Satellite Image" in html
    assert "Split Comparison" in html
    assert "Evidence View" in html


def test_basemap_switcher_and_disclaimer_present():
    """
    Verifies the basemap switcher with clear distinction between
    analysis imagery and reference basemap, including the exact disclaimer.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert 'id="imageSourceBadge"' in html
    assert 'id="btnToggleBasemap"' in html
    assert 'id="viewerBasemapImg"' in html
    assert "Reference basemap — not the image used for analysis." in html
    assert "Analysis Image: Sentinel-2 L2A" in html


def test_evidence_view_controls_and_filters():
    """
    Verifies that Evidence View controls include opacity slider (default 40%)
    and category filter pills (Water, Built-up, Vegetation, Uncertain).
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert 'id="evidenceControlsBar"' in html
    assert 'id="overlayOpacitySlider"' in html
    assert 'value="40"' in html  # 40% default opacity
    assert 'id="catBtnWater"' in html
    assert 'id="catBtnBuiltup"' in html
    assert 'id="catBtnVeg"' in html
    assert 'id="catBtnUncertain"' in html


def test_reference_basemap_api_endpoint():
    """
    Verifies the /api/reference-basemap endpoint contract.
    """
    resp = client.get("/api/reference-basemap")
    assert resp.status_code == 200
    data = resp.json()

    assert data["provider"] == "Esri World Imagery"
    assert "Reference basemap — not the image used for analysis." in data["disclaimer"]
    assert "tile_url" in data
    assert "https://" in data["tile_url"]


def test_copernicus_scene_authenticity_metadata():
    """
    Verifies that scene metadata includes all required authenticity fields:
    provider, sensor, scene_id, acquisition_date, aoi_bbox [min_lon, min_lat, max_lon, max_lat],
    resolution_m, analysis_trace_id.
    """
    res = copernicus_service.search_scenes("nepal", limit=2)
    scenes = res["scenes"]
    assert len(scenes) >= 1
    sc = scenes[0]

    assert "provider" in sc and ("Copernicus" in sc["provider"] or "ESA" in sc["provider"])
    assert "sensor" in sc and "MSI" in sc["sensor"]
    assert "scene_id" in sc
    assert "acquisition_date" in sc
    assert "resolution_m" in sc and sc["resolution_m"] == 10.0
    assert "aoi_bbox" in sc
    assert len(sc["aoi_bbox"]) == 4
    # BBOX is [min_lon, min_lat, max_lon, max_lat]
    min_lon, min_lat, max_lon, max_lat = sc["aoi_bbox"]
    assert min_lon < max_lon
    assert min_lat < max_lat
    assert "analysis_trace_id" in sc
    assert sc["analysis_trace_id"].startswith("trace-") or sc["analysis_trace_id"].startswith("SQ-")


def test_overlay_renderer_default_opacity_calibrated():
    """
    Verifies that OverlayRenderer default alpha is calibrated to 0.40 (40%),
    strictly satisfying the 35–45% requirement to preserve base satellite textures.
    """
    base_img = np.full((100, 100, 3), 120, dtype=np.uint8)
    mask = np.full((100, 100), CLASS_UNCHANGED, dtype=np.uint8)
    mask[20:50, 20:50] = CLASS_WATER_INCREASE

    change_res = ChangeClassificationResult(
        classified_mask=mask,
        delta_ndvi=np.zeros((100, 100), dtype=np.float32),
        delta_ndwi=np.zeros((100, 100), dtype=np.float32),
        delta_builtup=np.zeros((100, 100), dtype=np.float32),
        spectral_diff=np.zeros((100, 100), dtype=np.float32),
        builtup_mask=np.zeros((100, 100), dtype=bool),
        veg_increase_mask=np.zeros((100, 100), dtype=bool),
        veg_decrease_mask=np.zeros((100, 100), dtype=bool),
        water_increase_mask=(mask == CLASS_WATER_INCREASE),
        water_decrease_mask=np.zeros((100, 100), dtype=bool),
        cloud_mask=np.zeros((100, 100), dtype=bool)
    )

    res = render_evidence_overlay(base_img, change_res, add_decorations=False)
    blended = res.blended_image
    assert blended.shape == (100, 100, 3)

    # In the masked region, the base pixel (120) should NOT be completely overwritten (i.e. not purely mask color),
    # verifying semi-transparency.
    # Color for CLASS_WATER_INCREASE is (6, 182, 212)
    # Blended pixel should be ~ (1-0.4)*120 + 0.4*6 = 72 + 2 = 74
    val_r = blended[25, 25, 0]
    assert 60 <= val_r <= 90, f"Expected blended value around 74, got {val_r}"
    assert blended[25, 25, 0] != 120 and blended[25, 25, 0] != 6
    # Also verify the alpha channel of rgba_overlay is 40% (int(255 * 0.40) == 102)
    assert res.rgba_overlay[25, 25, 3] == int(255 * 0.40)


def test_nepal_flood_calibrated_wording():
    """
    Verifies that flood queries return calibrated scientific wording:
    'Possible newly water-covered area', 'detected from the selected satellite observations',
    and never claim 'exact flood boundary confirmed'.
    """
    res = copernicus_service.search_scenes("nepal", limit=2)
    scenes = res["scenes"]
    assert len(scenes) >= 2
    s1, s2 = scenes[0]["scene_id"], scenes[1]["scene_id"]

    resp = client.post(
        "/api/v1/analyze",
        data={
            "query": "Detect flood extent and water level rise in Nepal Koshi basin after heavy rainfall",
            "scene_ids": f"{s1},{s2}",
            "analysis_mode": "change"
        }
    )
    assert resp.status_code == 200
    res = resp.json()
    answer_text = res.get("result", {}).get("text_answer", "")
    summary_bullets = " ".join(res.get("result", {}).get("summary_bullet_points", []) or [])
    combined_output = f"{answer_text} {summary_bullets}"

    # Scientific calibration checks
    assert "Possible newly water-covered area" in combined_output
    assert "detected from the selected satellite observations" in combined_output
    assert "satellite-based change indicator, not an exact ground-confirmed flood boundary" in combined_output
    assert "Sentinel" in combined_output


def test_ap_buttons_removed_from_ui():
    """
    Verifies that the separate Andhra Pradesh state-wide button list has been removed
    from the UI display, allowing users to search any global or regional place cleanly.
    """
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.text

    assert "Andhra Pradesh State-Wide Coverage" not in html
    assert "Search ANY location or coordinates worldwide" in html


def test_rasuwa_bhote_koshi_search_and_real_optical_imagery():
    """
    Verifies that querying 'river corridor near Rasuwa / Bhote Koshi' returns
    authentic Sentinel-2 true-color satellite imagery of the Himalayan river corridor,
    never flat color masks or cartoon demo grids.
    """
    from PIL import Image
    from pathlib import Path

    resp = client.get("/api/copernicus/scenes?aoi_name=river%20corridor%20near%20Rasuwa%20%2F%20Bhote%20Koshi")
    assert resp.status_code == 200
    data = resp.json()

    assert "Rasuwa" in data["display_name"] or "Bhote Koshi" in data["display_name"]
    assert data["latitude"] == pytest.approx(28.17, abs=0.1)
    assert data["longitude"] == pytest.approx(85.48, abs=0.5)

    scenes = data.get("scenes", [])
    assert len(scenes) >= 2

    # Verify that the raster data is real optical satellite imagery (photographic richness)
    fpath = Path(scenes[0]["file_path"])
    assert fpath.exists()
    img = Image.open(fpath)
    arr = np.array(img)
    unique_colors = len(np.unique(arr.reshape(-1, arr.shape[-1]), axis=0))
    # Real satellite photos have thousands of subtle spectral reflectance values, not flat 2-6 color masks
    assert unique_colors > 1000, f"Expected realistic satellite photo (>1000 colors), got {unique_colors}"

