"""
SatQuery AI - Remote Sensing Change Statistics & Honest Quality-Aware Confidence Engine
Computes real spatial areas in hectares, quality indicators, and honest confidence scores without hallucination.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
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
class ChangeStatistics:
    """Rigorous physical hectare calculations and quality metrics."""
    area_of_interest_ha: float
    valid_area_ha: float
    changed_area_ha: float
    changed_percentage: float
    classes: Dict[str, float]  # category name -> hectares
    quality: Dict[str, Any]
    confidence_score: float
    confidence_label: str       # 'High confidence', 'Medium confidence', 'Low confidence'
    confidence_explanation: str
    simple_explanation: str


def compute_change_statistics(
    change_result: ChangeClassificationResult,
    resolution_m: float = 10.0,
    registration_quality: str = "good",
    overlap_percentage: float = 100.0,
    date_labels: Optional[Tuple[str, str]] = None,
    location_name: str = "this monitored area"
) -> ChangeStatistics:
    """
    Computes genuine hectare metrics from the classified raster mask.
    At 10m GSD, 1 pixel = 100 sq meters = 0.01 hectares.
    """
    mask = change_result.classified_mask
    total_pixels = mask.size
    ha_per_pixel = (resolution_m * resolution_m) / 10000.0

    # Class pixel counts
    builtup_count = int(np.sum(mask == CLASS_NEW_BUILTUP))
    veg_inc_count = int(np.sum(mask == CLASS_VEG_INCREASE))
    veg_dec_count = int(np.sum(mask == CLASS_VEG_DECREASE))
    water_inc_count = int(np.sum(mask == CLASS_WATER_INCREASE))
    water_dec_count = int(np.sum(mask == CLASS_WATER_DECREASE))
    cloud_count = int(np.sum(mask == CLASS_CLOUD_INVALID))
    unchanged_count = int(np.sum(mask == CLASS_UNCHANGED))

    valid_pixels = total_pixels - cloud_count
    changed_pixels = builtup_count + veg_inc_count + veg_dec_count + water_inc_count + water_dec_count

    # Calculate actual areas in hectares
    aoi_ha = round(total_pixels * ha_per_pixel, 1)
    valid_ha = round(valid_pixels * ha_per_pixel, 1)
    changed_ha = round(changed_pixels * ha_per_pixel, 1)
    changed_pct = round((changed_pixels / max(valid_pixels, 1)) * 100.0, 2)

    new_builtup_ha = round(builtup_count * ha_per_pixel, 1)
    veg_inc_ha = round(veg_inc_count * ha_per_pixel, 1)
    veg_dec_ha = round(veg_dec_count * ha_per_pixel, 1)
    water_inc_ha = round(water_inc_count * ha_per_pixel, 1)
    water_dec_ha = round(water_dec_count * ha_per_pixel, 1)

    classes_dict = {
        "new_builtup_ha": new_builtup_ha,
        "vegetation_increase_ha": veg_inc_ha,
        "vegetation_decrease_ha": veg_dec_ha,
        "water_increase_ha": water_inc_ha,
        "water_decrease_ha": water_dec_ha
    }

    valid_pct = round((valid_pixels / total_pixels) * 100.0, 1)
    cloud_pct = round((cloud_count / total_pixels) * 100.0, 1)

    quality_dict = {
        "valid_pixel_percentage": valid_pct,
        "cloud_masked_percentage": cloud_pct,
        "registration_quality": registration_quality,
        "overlap_percentage": round(overlap_percentage, 1),
        "ground_sample_distance_m": resolution_m
    }

    # Honest Quality-Aware Confidence Formula (Never fixed!)
    # confidence = 0.25 * Q_valid + 0.20 * Q_cloud + 0.20 * Q_overlap + 0.20 * Q_reg + 0.15 * Q_signal
    q_valid = min(1.0, max(0.0, valid_pct / 100.0))
    q_cloud = min(1.0, max(0.0, 1.0 - (cloud_pct / 60.0)))
    q_overlap = min(1.0, max(0.0, overlap_percentage / 100.0))
    
    reg_scores = {"good": 1.0, "fair": 0.80, "poor": 0.50}
    q_reg = reg_scores.get(registration_quality.lower(), 0.80)
    
    # Signal quality based on mean spectral difference
    sig_mean = float(np.mean(change_result.spectral_diff[mask != CLASS_CLOUD_INVALID])) if valid_pixels > 0 else 0.0
    q_signal = min(1.0, max(0.60, sig_mean / 0.15))

    raw_conf = (
        0.25 * q_valid
        + 0.20 * q_cloud
        + 0.20 * q_overlap
        + 0.20 * q_reg
        + 0.15 * q_signal
    )
    conf = round(float(np.clip(raw_conf, 0.45, 0.98)), 3)

    if conf >= 0.80:
        conf_label = "High confidence"
        conf_explanation = (
            f"High confidence ({conf*100:.1f}%): Both scenes have clear atmospheric conditions "
            f"({valid_pct}% valid pixels), solid overlap ({overlap_percentage}%), and good spatial co-registration."
        )
    elif conf >= 0.60:
        conf_label = "Medium confidence"
        conf_explanation = (
            f"Medium confidence ({conf*100:.1f}%): Analysis succeeded, but {cloud_pct}% cloud/shadow masking "
            f"or moderate scene overlap ({overlap_percentage}%) was detected. Local verification recommended."
        )
    else:
        conf_label = "Low confidence"
        conf_explanation = (
            f"Low confidence ({conf*100:.1f}%): High cloud contamination ({cloud_pct}%) or imperfect scene overlap "
            "affected the raster calculations. Check another scene pair if possible."
        )

    # Simple English Narrative
    d1_str = date_labels[0] if date_labels else "the first date"
    d2_str = date_labels[1] if date_labels else "the second date"

    # Identify primary change category
    dominant_cat = "minimal significant change"
    max_cat_ha = 0.0
    for name, ha_val in classes_dict.items():
        if ha_val > max_cat_ha:
            max_cat_ha = ha_val
            dominant_cat = name.replace("_ha", "").replace("_", " ")

    narrative = (
        f"We compared satellite scenes from {d1_str} and {d2_str} over {location_name}. "
        f"About {changed_pct}% of the valid land area ({changed_ha:.1f} hectares) shows noticeable difference. "
    )
    if new_builtup_ha > 0.5:
        narrative += f"Possible new built-up or paved surfaces cover about {new_builtup_ha:.1f} hectares (highlighted in red). "
    if veg_dec_ha > 0.5:
        narrative += f"Vegetation decline or crop harvesting covers about {veg_dec_ha:.1f} hectares (shown in yellow). "
    if veg_inc_ha > 0.5:
        narrative += f"Vegetation growth covers about {veg_inc_ha:.1f} hectares (shown in green). "
    if water_inc_ha > 0.5:
        narrative += f"Water surface expansion covers about {water_inc_ha:.1f} hectares (shown in cyan-blue). "

    if cloud_pct > 5.0:
        narrative += f"About {cloud_pct}% of the image was covered by clouds or invalid pixels. "
    narrative += "These indicators should be confirmed with local on-ground knowledge before making official decisions."

    return ChangeStatistics(
        area_of_interest_ha=aoi_ha,
        valid_area_ha=valid_ha,
        changed_area_ha=changed_ha,
        changed_percentage=changed_pct,
        classes=classes_dict,
        quality=quality_dict,
        confidence_score=conf,
        confidence_label=conf_label,
        confidence_explanation=conf_explanation,
        simple_explanation=narrative
    )
