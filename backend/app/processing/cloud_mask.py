"""
SatQuery AI - Remote Sensing Cloud & Invalid-Pixel Masking
Detects cloud contamination, cirrus, shadows, and no-data borders using Sentinel-2 SCL or spectral thresholds.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
import numpy as np

from backend.app.processing.raster_loader import RasterScene


@dataclass
class CloudMaskResult:
    """Output of cloud and quality masking."""
    mask: np.ndarray  # boolean 2D array, True = cloud/shadow/invalid (masked out)
    valid_mask: np.ndarray  # boolean 2D array, True = clear, valid pixel for analysis
    valid_pixel_percentage: float
    cloud_masked_percentage: float
    has_cloud_warning: bool
    warning: Optional[str] = None


def compute_cloud_mask(
    scene: RasterScene,
    scl_layer: Optional[np.ndarray] = None,
    cloud_threshold: float = 0.55
) -> CloudMaskResult:
    """
    Computes a pixel-level cloud, shadow, and no-data mask for a given satellite scene.
    """
    h, w = scene.height, scene.width
    total_pixels = h * w

    # 1. Check if official Sentinel-2 Scene Classification Layer (SCL) is provided
    if scl_layer is not None:
        # SCL Values:
        # 0: NO_DATA, 1: SATURATED_OR_DEFECTIVE, 2: DARK_AREA_PIXELS
        # 3: CLOUD_SHADOWS, 8: CLOUD_MEDIUM_PROBABILITY, 9: CLOUD_HIGH_PROBABILITY
        # 10: THIN_CIRRUS, 11: SNOW
        cloud_pixels = np.isin(scl_layer, [0, 1, 3, 8, 9, 10, 11])
    else:
        # 2. Spectral heuristic masking for Sentinel-2 Level-2A reflectance [0.0, 1.0]
        r = scene.red
        g = scene.green
        b = scene.blue
        brightness = (r + g + b) / 3.0

        # High brightness in all visible bands with low color saturation (white/gray cloud signature)
        visible_max = np.maximum(np.maximum(r, g), b)
        visible_min = np.minimum(np.minimum(r, g), b)
        whiteness = 1.0 - ((visible_max - visible_min) / (visible_max + 1e-5))

        # Cloud core: genuine clouds have extreme brightness (> 0.88) AND are spectrally neutral/white
        # Buildings, roads, and sand have distinct spectral gradients (e.g. red > blue) and are NOT clouds.
        cloud_core = (brightness > 0.88) & (whiteness > 0.90) & (b > 0.80)
        cloud_opaque = (brightness > 0.92) & (r > 0.85) & (b > 0.85)

        # No-data black borders (all bands identically 0)
        no_data = (r == 0) & (g == 0) & (b == 0)

        cloud_pixels = cloud_core | cloud_opaque | no_data

    cloud_count = int(np.sum(cloud_pixels))
    cloud_pct = round((cloud_count / total_pixels) * 100.0, 1)
    valid_pct = round(100.0 - cloud_pct, 1)

    has_warning = cloud_pct > 20.0
    warning = (
        f"Cloud contamination detected: {cloud_pct}% of the scene was masked out. "
        "Results in cloudy regions may require verification."
        if has_warning else None
    )

    return CloudMaskResult(
        mask=cloud_pixels,
        valid_mask=~cloud_pixels,
        valid_pixel_percentage=valid_pct,
        cloud_masked_percentage=cloud_pct,
        has_cloud_warning=has_warning,
        warning=warning
    )


def compute_joint_cloud_mask(
    scene1: RasterScene,
    scene2: RasterScene
) -> CloudMaskResult:
    """
    Computes a combined cloud and validity mask across two multi-temporal scenes.
    A pixel is valid for change detection ONLY if it is clear and valid in BOTH scenes.
    """
    m1 = compute_cloud_mask(scene1)
    m2 = compute_cloud_mask(scene2)

    joint_mask = m1.mask | m2.mask
    valid_mask = ~joint_mask

    total_pixels = joint_mask.size
    cloud_count = int(np.sum(joint_mask))
    cloud_pct = round((cloud_count / total_pixels) * 100.0, 1)
    valid_pct = round(100.0 - cloud_pct, 1)

    has_warning = cloud_pct > 25.0
    warning = None
    if has_warning:
        warning = f"Combined cloud/shadow masking removed {cloud_pct}% of the comparison area. Use results with caution."

    return CloudMaskResult(
        mask=joint_mask,
        valid_mask=valid_mask,
        valid_pixel_percentage=valid_pct,
        cloud_masked_percentage=cloud_pct,
        has_cloud_warning=has_warning,
        warning=warning
    )
