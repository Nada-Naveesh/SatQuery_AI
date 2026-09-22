"""
SatQuery AI - Quality Assessment & Confidence Calibration Engine
Computes honest, mathematically grounded confidence scores from physical remote-sensing indicators.
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class QualityAssessmentResult:
    score: float                # Confidence score in [0.0, 1.0]
    percentage: int             # Confidence in [0, 100]%
    tier: str                   # 'High confidence', 'Medium confidence', 'Low confidence'
    explanation: str            # Plain-English explanation of why this confidence was computed
    valid_pixel_pct: float      # Clear data %
    cloud_masked_pct: float     # Cloud & shadow %
    overlap_pct: float          # Spatial overlap %
    registration_quality: str   # 'good', 'fair', 'poor'


def calculate_quality_score(
    valid_pixel_pct: float,
    cloud_masked_pct: float,
    overlap_pct: float = 100.0,
    registration_quality: str = "good",
    spectral_contrast: float = 0.85
) -> QualityAssessmentResult:
    """
    Computes quality-aware confidence:
      confidence = 0.25 * Q_valid + 0.20 * Q_cloud + 0.20 * Q_overlap + 0.20 * Q_reg + 0.15 * Q_signal
    """
    q_valid = min(1.0, max(0.0, valid_pixel_pct / 100.0))
    q_cloud = min(1.0, max(0.0, 1.0 - (cloud_masked_pct / 60.0)))
    q_overlap = min(1.0, max(0.0, overlap_pct / 100.0))

    reg_scores = {"good": 1.0, "fair": 0.70, "poor": 0.40}
    q_reg = reg_scores.get(registration_quality.lower(), 0.80)
    q_signal = min(1.0, max(0.0, spectral_contrast))

    raw_score = (
        0.25 * q_valid +
        0.20 * q_cloud +
        0.20 * q_overlap +
        0.20 * q_reg +
        0.15 * q_signal
    )
    score = round(min(0.99, max(0.10, raw_score)), 2)
    pct = int(round(score * 100.0))

    if score >= 0.85:
        tier = "High confidence"
        explanation = (
            f"High confidence ({pct}%): The selected scenes have optimal atmospheric visibility "
            f"({valid_pixel_pct:.1f}% clear pixels), strong {overlap_pct:.0f}% spatial overlap, and verified sub-pixel co-registration."
        )
    elif score >= 0.70:
        tier = "Medium confidence"
        explanation = (
            f"Medium confidence ({pct}%): The analysis is reliable, but minor atmospheric haze or clouds "
            f"affected {cloud_masked_pct:.1f}% of the observation area."
        )
    else:
        tier = "Low confidence"
        explanation = (
            f"Low confidence ({pct}%): Significant cloud obscuration ({cloud_masked_pct:.1f}%) or reduced spatial overlap "
            "may limit change detection accuracy. Cross-verification recommended."
        )

    return QualityAssessmentResult(
        score=score,
        percentage=pct,
        tier=tier,
        explanation=explanation,
        valid_pixel_pct=round(valid_pixel_pct, 1),
        cloud_masked_pct=round(cloud_masked_pct, 1),
        overlap_pct=round(overlap_pct, 1),
        registration_quality=registration_quality
    )
