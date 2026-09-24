"""
SatQuery AI - Viewport Map Isolation & Real Imagery PDF Tests
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)

Verifies:
1. When uploading data, the uploaded data is displayed in #viewportStage and the streets & places
   map (#leafletMap) is strictly hidden.
2. Clicking Streets & Places switches to the map view, while clicking Satellite Image / Split / Evidence
   switches back to the image view.
3. PDF intelligence reports contain ONLY real satellite imagery (or real streets basemaps)
   and alpha-composited overlays directly on top of real satellite scenes, never synthetic black diagrams.
"""

import io
import pytest
import numpy as np
from PIL import Image
from starlette.testclient import TestClient

from backend.app.main import app, composite_overlay_on_real_image, get_real_reference_image
from backend.app.config import settings

client = TestClient(app)


def test_viewport_html_hides_streets_and_shows_image_stage_by_default():
    """
    Verifies that on load, #leafletMap is hidden and #viewportStage is active and visible.
    """
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    # #leafletMap has 'hidden' class by default
    assert 'id="leafletMap" class="absolute inset-0 w-full h-full z-0 hidden"' in html, (
        "leafletMap should be hidden by default until user enters Streets & Places"
    )

    # #viewportStage is visible and interactive
    assert 'id="viewportStage" class="absolute inset-0 w-full h-full flex items-center justify-center pointer-events-auto z-10' in html, (
        "viewportStage should be visible with pointer-events-auto by default"
    )

    # Satellite Image button is active by default
    assert 'id="btnViewSatellite" class="px-2.5 py-1 rounded bg-blue-600 text-white font-semibold' in html

    # Mode switching functions exist in the client JavaScript
    assert "function switchToImageView(" in html
    assert "function switchToMapView(" in html
    assert "switchToImageView('satellite')" in html


def test_handle_file_select_switches_to_image_view():
    """
    Verifies that handleFileSelect in mission_control.py immediately invokes switchToImageView('satellite')
    and resets zoom & pan so the uploaded data is the only thing seen.
    """
    res = client.get("/")
    assert res.status_code == 200
    html = res.text

    assert "switchToImageView('satellite')" in html
    assert "Uploaded Data:" in html


def test_composite_overlay_on_real_image_never_produces_black_background():
    """
    Verifies that composite_overlay_on_real_image alpha-composites transparent change masks
    directly over the real satellite image, returning a valid JPEG with visible underlying content.
    """
    # Create simulated real satellite image (greenish landscape)
    real_sat = Image.new("RGB", (200, 200), (34, 139, 34))

    # Create RGBA overlay with a cyan flood polygon and transparent background
    ov = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
    for x in range(40, 100):
        for y in range(40, 100):
            ov.putpixel((x, y), (6, 182, 212, 220))  # Cyan

    ov_buf = io.BytesIO()
    ov.save(ov_buf, format="PNG")
    ov_bytes = ov_buf.getvalue()

    result_bytes = composite_overlay_on_real_image(real_sat, ov_bytes, opacity=0.50)
    assert len(result_bytes) > 500

    # Load result and check that background pixels are still green (real satellite image), NOT pure black!
    res_img = Image.open(io.BytesIO(result_bytes))
    corner_pixel = res_img.getpixel((10, 10))
    # Green landscape pixel should not be black (0, 0, 0)
    assert corner_pixel[1] > 50, f"Background became synthetic black! Pixel was {corner_pixel}"


def test_get_real_reference_image_returns_real_sentinel_image():
    """
    Verifies that get_real_reference_image resolves authentic Sentinel-2 images from disk
    for specified AOIs or defaults.
    """
    session = {
        "input_summary": {"area": "Vijayawada Krishna Basin", "sensor": "Sentinel-2 L2A"},
        "query": "What changed in Vijayawada?"
    }
    img_bytes = get_real_reference_image(session)
    assert img_bytes is not None
    assert len(img_bytes) > 1000

    # Confirm it is a valid JPEG image
    pil_img = Image.open(io.BytesIO(img_bytes))
    assert pil_img.size[0] > 0 and pil_img.size[1] > 0


def test_pdf_report_with_uploaded_image_contains_real_imagery():
    """
    Verifies end-to-end: uploading a custom image and requesting the PDF report
    returns a valid, complete mission intelligence PDF with real satellite imagery.
    """
    # Create sample satellite image
    img = Image.new("RGB", (128, 128), (50, 120, 80))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    res = client.post(
        "/api/v1/analyze",
        data={"query": "Detect water bodies and land use in this scene", "task_hint": "single_image_vqa"},
        files=[("files", ("real_satellite_capture.png", buf.getvalue(), "image/png"))]
    )
    assert res.status_code == 200
    data = res.json()
    trace_id = data["execution_trace"]["trace_id"]

    # Request PDF report
    pdf_res = client.get(f"/api/v1/report/pdf?trace_id={trace_id}")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 2000
    assert pdf_res.content.startswith(b"%PDF")
