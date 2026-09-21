"""
SatQuery AI - Geospatial Spatial Alignment & Co-Registration
Ensures pixel-grid alignment, CRS consistency, and spatial overlap between multi-temporal scenes.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
import numpy as np
from PIL import Image

from backend.app.processing.raster_loader import RasterScene


@dataclass
class AlignmentResult:
    """Output of the spatial alignment pipeline."""
    scene1: RasterScene
    scene2: RasterScene
    registration_quality: str  # 'good', 'fair', 'poor'
    overlap_percentage: float
    aligned_height: int
    aligned_width: int
    warning: Optional[str] = None


def align_scenes(
    scene1: RasterScene,
    scene2: RasterScene,
    target_dim: Optional[Tuple[int, int]] = None
) -> AlignmentResult:
    """
    Co-registers two multi-temporal scenes into an identical pixel analysis grid.
    If spatial dimensions or channels differ, resamples cleanly using bilinear interpolation.
    """
    h1, w1 = scene1.height, scene1.width
    h2, w2 = scene2.height, scene2.width

    target_h, target_w = target_dim or (h2, w2)
    warning = None
    quality = "good"
    overlap_pct = 100.0

    # Bounding box overlap estimation if available
    if scene1.bbox and scene2.bbox:
        b1 = scene1.bbox
        b2 = scene2.bbox
        # Format: [min_lat, min_lon, max_lat, max_lon]
        inter_min_lat = max(b1[0], b2[0])
        inter_min_lon = max(b1[1], b2[1])
        inter_max_lat = min(b1[2], b2[2])
        inter_max_lon = min(b1[3], b2[3])

        if inter_min_lat >= inter_max_lat or inter_min_lon >= inter_max_lon:
            overlap_pct = 0.0
            quality = "poor"
            warning = "These scenes cover different geographic areas. The comparison may be unreliable."
        else:
            area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
            inter_area = (inter_max_lat - inter_min_lat) * (inter_max_lon - inter_min_lon)
            overlap_pct = min(100.0, max(0.0, (inter_area / max(area1, 1e-6)) * 100.0))
            if overlap_pct < 60.0:
                quality = "fair"
                warning = f"Scene overlap is limited ({overlap_pct:.1f}%). Edge artifacts may appear."

    # Resample scene 1 if needed
    if (h1, w1) != (target_h, target_w):
        quality = "fair" if quality == "good" else quality
        resampled_data = np.zeros((target_h, target_w, scene1.num_channels), dtype=np.float32)
        for c in range(scene1.num_channels):
            band_img = Image.fromarray((scene1.data[:, :, c] * 255.0).astype(np.uint8))
            resampled_band = band_img.resize((target_w, target_h), Image.BILINEAR)
            resampled_data[:, :, c] = np.array(resampled_band, dtype=np.float32) / 255.0

        tc_img = Image.fromarray(scene1.true_color).resize((target_w, target_h), Image.BILINEAR)
        resampled_tc = np.array(tc_img, dtype=np.uint8)

        s1_aligned = RasterScene(
            data=resampled_data,
            channels=scene1.channels,
            height=target_h,
            width=target_w,
            num_channels=scene1.num_channels,
            resolution_m=scene2.resolution_m,
            crs=scene2.crs,
            bbox=scene1.bbox,
            true_color=resampled_tc
        )
    else:
        s1_aligned = scene1

    # Resample scene 2 if needed (e.g. when target_dim specified)
    if (h2, w2) != (target_h, target_w):
        resampled_data2 = np.zeros((target_h, target_w, scene2.num_channels), dtype=np.float32)
        for c in range(scene2.num_channels):
            band_img2 = Image.fromarray((scene2.data[:, :, c] * 255.0).astype(np.uint8))
            resampled_band2 = band_img2.resize((target_w, target_h), Image.BILINEAR)
            resampled_data2[:, :, c] = np.array(resampled_band2, dtype=np.float32) / 255.0

        tc_img2 = Image.fromarray(scene2.true_color).resize((target_w, target_h), Image.BILINEAR)
        resampled_tc2 = np.array(tc_img2, dtype=np.uint8)

        s2_aligned = RasterScene(
            data=resampled_data2,
            channels=scene2.channels,
            height=target_h,
            width=target_w,
            num_channels=scene2.num_channels,
            resolution_m=scene2.resolution_m,
            crs=scene2.crs,
            bbox=scene2.bbox,
            true_color=resampled_tc2
        )
    else:
        s2_aligned = scene2

    return AlignmentResult(
        scene1=s1_aligned,
        scene2=s2_aligned,
        registration_quality=quality,
        overlap_percentage=round(overlap_pct, 1),
        aligned_height=target_h,
        aligned_width=target_w,
        warning=warning
    )
