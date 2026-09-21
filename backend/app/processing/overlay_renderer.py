"""
SatQuery AI - Remote Sensing Evidence Overlay Renderer
Renders scientifically accurate, colorized change overlays directly on top of satellite imagery.
Supports both composite blended imagery and transparent RGBA overlays with layer opacity controls.
"""

import io
import base64
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from backend.app.processing.change_detection import (
    ChangeClassificationResult,
    CLASS_UNCHANGED,
    CLASS_NEW_BUILTUP,
    CLASS_VEG_INCREASE,
    CLASS_VEG_DECREASE,
    CLASS_WATER_INCREASE,
    CLASS_WATER_DECREASE,
    CLASS_CLOUD_INVALID
)

# Standardized Remote Sensing Change Class Color Palette (RGB)
COLOR_PALETTE: Dict[int, Tuple[int, int, int]] = {
    CLASS_NEW_BUILTUP: (239, 68, 68),      # Crimson Red (#ef4444)
    CLASS_VEG_INCREASE: (34, 197, 94),     # Emerald Green (#22c55e)
    CLASS_VEG_DECREASE: (234, 179, 8),     # Amber/Yellow (#eab308)
    CLASS_WATER_INCREASE: (6, 182, 212),   # Cyan/Blue (#06b6d4)
    CLASS_WATER_DECREASE: (168, 85, 247),  # Purple (#a855f7)
    CLASS_CLOUD_INVALID: (120, 120, 130),  # Neutral Gray
}


@dataclass
class RenderResult:
    """Output containing visual evidence products."""
    blended_image: np.ndarray      # uint8 (H, W, 3) - Satellite image + colored change overlay
    rgba_overlay: np.ndarray       # uint8 (H, W, 4) - Pure transparent overlay for client slider
    overlay_base64: str            # Data URI of blended image (or RGBA)
    rgba_base64: str               # Data URI of transparent RGBA overlay


def render_evidence_overlay(
    base_true_color: np.ndarray,
    change_result: ChangeClassificationResult,
    alpha: float = 0.65,
    add_decorations: bool = True,
    date_labels: Optional[Tuple[str, str]] = None,
    resolution_m: float = 10.0
) -> RenderResult:
    """
    Renders the classified change mask as an authentic, alpha-blended remote sensing evidence overlay.
    """
    h, w = base_true_color.shape[:2]
    mask = change_result.classified_mask

    # 1. Create Transparent RGBA Overlay Layer
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    # Blend on base image
    blended = base_true_color.copy().astype(np.float32)

    for class_id, color in COLOR_PALETTE.items():
        class_pixels = (mask == class_id)
        if not np.any(class_pixels):
            continue

        c_r, c_g, c_b = color
        color_arr = np.array([c_r, c_g, c_b], dtype=np.float32)

        # RGBA Layer: assign color and alpha
        a_val = int(255 * (0.40 if class_id == CLASS_CLOUD_INVALID else alpha))
        rgba[class_pixels, 0] = c_r
        rgba[class_pixels, 1] = c_g
        rgba[class_pixels, 2] = c_b
        rgba[class_pixels, 3] = a_val

        # Blended RGB Layer: Alpha-blend over base satellite image
        class_alpha = 0.35 if class_id == CLASS_CLOUD_INVALID else alpha
        blended[class_pixels] = (
            (1.0 - class_alpha) * blended[class_pixels] + class_alpha * color_arr
        )

    blended_uint8 = np.clip(blended, 0, 255).astype(np.uint8)

    # 2. Add Tactical Remote Sensing Visual Accents (North arrow, scale bar) if requested
    if add_decorations and h >= 256 and w >= 256:
        pil_img = Image.fromarray(blended_uint8)
        draw = ImageDraw.Draw(pil_img)

        # Draw North Arrow (top right)
        nx, ny = w - 35, 30
        draw.polygon([(nx, ny - 15), (nx - 7, ny + 5), (nx + 7, ny + 5)], fill=(239, 68, 68))
        draw.polygon([(nx, ny - 15), (nx + 7, ny + 5), (nx, ny + 2)], fill=(200, 30, 30))
        draw.text((nx - 4, ny + 7), "N", fill=(255, 255, 255))

        # Draw Scale Bar (bottom left)
        # For 10m GSD, 50 pixels = 500 meters
        scale_px = int(500.0 / max(resolution_m, 1.0))
        if scale_px < w // 3:
            sx, sy = 25, h - 25
            draw.rectangle([sx, sy, sx + scale_px, sy + 3], fill=(255, 255, 255))
            draw.text((sx, sy - 14), "500 m", fill=(255, 255, 255))

        # Draw acquisition dates label (top left) if provided
        if date_labels:
            d1, d2 = date_labels
            date_text = f"T1: {d1}  vs  T2: {d2}"
            draw.rectangle([10, 10, 10 + len(date_text) * 7, 26], fill=(13, 13, 18, 190))
            draw.text((14, 12), date_text, fill=(240, 240, 240))

        blended_uint8 = np.array(pil_img)

    # 3. Base64 Encode both outputs
    def _to_b64(arr: np.ndarray, fmt: str = "PNG") -> str:
        p = Image.fromarray(arr)
        buf = io.BytesIO()
        p.save(buf, format=fmt)
        b = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b}"

    return RenderResult(
        blended_image=blended_uint8,
        rgba_overlay=rgba,
        overlay_base64=_to_b64(blended_uint8),
        rgba_base64=_to_b64(rgba)
    )
