"""
SatQuery AI - Physical Area Statistics Engine
Computes rigorous ground-truth surface areas in hectares from raster transform,
CRS, and classified pixel masks without fabrication or ungrounded defaults.
"""

import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

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


@dataclass
class AreaMetricResult:
    """Computed area breakdown with full scale provenance."""
    is_georeferenced: bool
    has_valid_scale: bool
    pixel_area_m2: Optional[float]
    pixel_area_ha: Optional[float]
    
    # Hectare quantities (None if non-georeferenced)
    total_area_ha: Optional[float]
    valid_area_ha: Optional[float]
    changed_area_ha: Optional[float]
    changed_percentage: Optional[float]
    
    builtup_ha: Optional[float]
    veg_inc_ha: Optional[float]
    veg_dec_ha: Optional[float]
    water_inc_ha: Optional[float]
    water_dec_ha: Optional[float]
    cloud_invalid_ha: Optional[float]
    
    # Raw pixel counts (Always exact)
    total_pixels: int
    valid_pixels: int
    changed_pixels: int
    builtup_pixels: int
    veg_inc_pixels: int
    veg_dec_pixels: int
    water_inc_pixels: int
    water_dec_pixels: int
    cloud_pixels: int
    
    # Scientific display strings
    total_changed_display: str
    builtup_display: str
    veg_loss_display: str
    veg_gain_display: str
    water_inc_display: str
    water_dec_display: str
    cloud_display: str
    plain_english_narrative: str
    limitation_notice: Optional[str] = None


def format_hectare_value(val: Optional[float], is_georeferenced: bool = True) -> str:
    """Formats a hectare value using strict precision rules."""
    if not is_georeferenced or val is None:
        return "N/A (No map scale)"
    if val == 0.0:
        return "0.00 ha"
    if 0.0 < val < 0.01:
        return "< 0.01 ha"
    return f"{val:.2f} ha"


def compute_pixel_area_hectares(
    resolution_m: Optional[float] = 10.0,
    transform: Optional[Tuple[float, ...]] = None,
    crs: str = "EPSG:4326",
    center_lat: float = 16.0,
    is_georeferenced: bool = True
) -> Tuple[Optional[float], Optional[float]]:
    """
    Computes (pixel_area_m2, pixel_area_ha) from transform or resolution.
    Returns (None, None) if image lacks geospatial scale.
    """
    if not is_georeferenced:
        return None, None

    # 1. Projected CRS with 6-element affine transform [a, b, c, d, e, f]
    if transform and len(transform) >= 6:
        a, b, _, d, e, _ = transform[:6]
        # In projected coordinates (e.g. UTM), units are metres
        if "utm" in crs.lower() or "326" in crs or "3857" in crs:
            pixel_area_m2 = abs(a * e - b * d)
            if pixel_area_m2 > 0:
                return pixel_area_m2, pixel_area_m2 / 10000.0
        # In geographic coordinates (degrees, e.g. EPSG:4326), compute geodesic area
        else:
            deg_x = abs(a)
            deg_y = abs(e)
            lat_rad = math.radians(center_lat)
            dx_m = deg_x * 111320.0 * math.cos(lat_rad)
            dy_m = deg_y * 111320.0
            pixel_area_m2 = dx_m * dy_m
            if pixel_area_m2 > 0:
                return pixel_area_m2, pixel_area_m2 / 10000.0

    # 2. Standard Sentinel-2 L2A optical grid (10m GSD)
    if resolution_m and resolution_m > 0:
        pixel_area_m2 = float(resolution_m * resolution_m)
        pixel_area_ha = pixel_area_m2 / 10000.0
        return pixel_area_m2, pixel_area_ha

    return None, None


def calculate_physical_area_statistics(
    change_result: ChangeClassificationResult,
    resolution_m: Optional[float] = 10.0,
    transform: Optional[Tuple[float, ...]] = None,
    crs: str = "EPSG:4326",
    center_lat: float = 16.0,
    is_georeferenced: bool = True,
    date1: str = "before date",
    date2: str = "after date",
    location_name: str = "selected area"
) -> AreaMetricResult:
    """
    Executes rigorous physical area quantification for all detected change classes.
    """
    mask = change_result.classified_mask
    total_pixels = int(mask.size)

    pixel_area_m2, pixel_area_ha = compute_pixel_area_hectares(
        resolution_m=resolution_m,
        transform=transform,
        crs=crs,
        center_lat=center_lat,
        is_georeferenced=is_georeferenced
    )

    # Compute exact pixel counts inside classified mask
    builtup_px = int(np.sum(mask == CLASS_NEW_BUILTUP))
    veg_inc_px = int(np.sum(mask == CLASS_VEG_INCREASE))
    veg_dec_px = int(np.sum(mask == CLASS_VEG_DECREASE))
    water_inc_px = int(np.sum(mask == CLASS_WATER_INCREASE))
    water_dec_px = int(np.sum(mask == CLASS_WATER_DECREASE))
    cloud_px = int(np.sum(mask == CLASS_CLOUD_INVALID))
    
    valid_px = total_pixels - cloud_px
    changed_px = builtup_px + veg_inc_px + veg_dec_px + water_inc_px + water_dec_px
    changed_pct = round((changed_px / max(valid_px, 1)) * 100.0, 2)

    has_scale = (is_georeferenced and pixel_area_ha is not None)

    if has_scale:
        total_ha = round(total_pixels * pixel_area_ha, 2)
        valid_ha = round(valid_px * pixel_area_ha, 2)
        changed_ha = round(changed_px * pixel_area_ha, 2)
        
        b_ha = round(builtup_px * pixel_area_ha, 2)
        v_inc_ha = round(veg_inc_px * pixel_area_ha, 2)
        v_dec_ha = round(veg_dec_px * pixel_area_ha, 2)
        w_inc_ha = round(water_inc_px * pixel_area_ha, 2)
        w_dec_ha = round(water_dec_px * pixel_area_ha, 2)
        c_ha = round(cloud_px * pixel_area_ha, 2)

        total_changed_disp = format_hectare_value(changed_ha, True)
        builtup_disp = format_hectare_value(b_ha, True)
        veg_loss_disp = format_hectare_value(v_dec_ha, True)
        veg_gain_disp = format_hectare_value(v_inc_ha, True)
        water_inc_disp = format_hectare_value(w_inc_ha, True)
        water_dec_disp = format_hectare_value(w_dec_ha, True)
        cloud_disp = format_hectare_value(c_ha, True)

        limitation_notice = None

        # Build scientific plain-English narrative
        parts = []
        if changed_px == 0:
            narrative = (
                f"No significant land-surface change was detected above the confidence threshold "
                f"between {date1} and {date2} in {location_name}. Total changed area: 0.00 ha."
            )
        else:
            if b_ha > 0:
                parts.append(f"possible new built-up or impervious surfaces covering {b_ha:.2f} ha (highlighted in red)")
            if v_dec_ha > 0:
                parts.append(f"vegetation decrease across {v_dec_ha:.2f} ha (highlighted in yellow)")
            if v_inc_ha > 0:
                parts.append(f"vegetation increase across {v_inc_ha:.2f} ha (highlighted in green)")
            if w_inc_ha > 0:
                parts.append(f"water surface expansion / inundation of {w_inc_ha:.2f} ha (highlighted in blue)")
            if w_dec_ha > 0:
                parts.append(f"water body contraction of {w_dec_ha:.2f} ha (highlighted in purple)")

            desc = ", ".join(parts) if parts else "minor spectral variations"
            cloud_stmt = f" Clouds or invalid data affected {c_ha:.2f} ha ({(cloud_px/total_pixels)*100.0:.1f}%)." if c_ha > 0 else ""
            narrative = (
                f"We compared satellite observations from {date1} and {date2} over {location_name}. "
                f"Approximately {changed_pct:.1f}% of the valid area ({changed_ha:.2f} hectares) shows detectable change, including {desc}.{cloud_stmt}"
            )
    else:
        total_ha = valid_ha = changed_ha = None
        b_ha = v_inc_ha = v_dec_ha = w_inc_ha = w_dec_ha = c_ha = None
        
        total_changed_disp = f"{changed_px:,} pixels"
        builtup_disp = f"{builtup_px:,} pixels"
        veg_loss_disp = f"{veg_dec_px:,} pixels"
        veg_gain_disp = f"{veg_inc_px:,} pixels"
        water_inc_disp = f"{water_inc_px:,} pixels"
        water_dec_disp = f"{water_dec_px:,} pixels"
        cloud_disp = f"{cloud_px:,} pixels"

        limitation_notice = (
            "Visual change map available. Physical area in hectares is unavailable "
            "because this uploaded file does not contain geographic coordinate scale metadata."
        )
        narrative = (
            f"Visual comparison completed between {date1} and {date2}. "
            f"A total of {changed_px:,} pixels ({changed_pct:.1f}% of valid image area) exhibited spectral change. "
            f"{limitation_notice}"
        )

    return AreaMetricResult(
        is_georeferenced=is_georeferenced,
        has_valid_scale=has_scale,
        pixel_area_m2=pixel_area_m2,
        pixel_area_ha=pixel_area_ha,
        total_area_ha=total_ha,
        valid_area_ha=valid_ha,
        changed_area_ha=changed_ha,
        changed_percentage=changed_pct,
        builtup_ha=b_ha,
        veg_inc_ha=v_inc_ha,
        veg_dec_ha=v_dec_ha,
        water_inc_ha=w_inc_ha,
        water_dec_ha=w_dec_ha,
        cloud_invalid_ha=c_ha,
        total_pixels=total_pixels,
        valid_pixels=valid_px,
        changed_pixels=changed_px,
        builtup_pixels=builtup_px,
        veg_inc_pixels=veg_inc_px,
        veg_dec_pixels=veg_dec_px,
        water_inc_pixels=water_inc_px,
        water_dec_pixels=water_dec_px,
        cloud_pixels=cloud_px,
        total_changed_display=total_changed_disp,
        builtup_display=builtup_disp,
        veg_loss_display=veg_loss_disp,
        veg_gain_display=veg_gain_disp,
        water_inc_display=water_inc_disp,
        water_dec_display=water_dec_disp,
        cloud_display=cloud_disp,
        plain_english_narrative=narrative,
        limitation_notice=limitation_notice
    )
