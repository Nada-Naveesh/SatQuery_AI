"""
SatQuery AI - Test WebP Format Upload Support
Verifies that .webp image files (including Copernicus True Color exports)
are accepted and processed through /api/v1/analyze without unsupported extension errors.
"""

import io
import pytest
from PIL import Image
from starlette.testclient import TestClient
from backend.app.main import app
from backend.app.validators import ALLOWED_EXTENSIONS

client = TestClient(app)


def test_allowed_extensions_includes_webp():
    """Verify that .webp is explicitly permitted in ALLOWED_EXTENSIONS."""
    assert ".webp" in ALLOWED_EXTENSIONS, ".webp must be in ALLOWED_EXTENSIONS"


def test_analyze_endpoint_accepts_webp_file():
    """Create a synthetic WebP image and verify 200 OK from /api/v1/analyze."""
    img = Image.new("RGB", (256, 256), color=(40, 80, 150))
    buf = io.BytesIO()
    img.save(buf, format="WEBP")
    webp_bytes = buf.getvalue()

    files = [
        ("files", ("2026-09-23-00_00_2026-09-23-23_59_Sentinel-2_L2A_True_color.webp", io.BytesIO(webp_bytes), "image/webp"))
    ]
    data = {
        "query": "What land cover types are visible in this satellite scene?",
        "input_mode": "single_optical"
    }

    res = client.post("/api/v1/analyze", data=data, files=files)
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}: {res.text}"
    body = res.json()
    assert "detected_task" in body
    assert "result" in body
    assert "text_answer" in body["result"]
    assert len(body["result"]["text_answer"]) > 0
