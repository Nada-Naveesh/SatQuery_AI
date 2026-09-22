"""
SatQuery AI - Remote Sensing Raster Processing & Evidence Generation Engine
Smart India Hackathon 2026 | PS 26167 (ISRO / Department of Space)
"""

from backend.app.processing.raster_loader import load_raster_scene, RasterScene
from backend.app.processing.alignment import align_scenes, AlignmentResult
from backend.app.processing.cloud_mask import compute_cloud_mask, compute_joint_cloud_mask, CloudMaskResult
from backend.app.processing.indices import compute_spectral_indices, SpectralIndices
from backend.app.processing.change_detection import (
    detect_surface_changes,
    ChangeClassificationResult,
    CLASS_UNCHANGED,
    CLASS_NEW_BUILTUP,
    CLASS_VEG_INCREASE,
    CLASS_VEG_DECREASE,
    CLASS_WATER_INCREASE,
    CLASS_WATER_DECREASE,
    CLASS_CLOUD_INVALID
)
from backend.app.processing.overlay_renderer import render_evidence_overlay, RenderResult, COLOR_PALETTE
from backend.app.processing.statistics import compute_change_statistics, ChangeStatistics
from backend.app.processing.area_stats import calculate_physical_area_statistics, AreaMetricResult, compute_pixel_area_hectares
from backend.app.processing.quality_score import calculate_quality_score, QualityAssessmentResult
from backend.app.processing.validation import validate_analysis_input

__all__ = [
    "load_raster_scene",
    "RasterScene",
    "align_scenes",
    "AlignmentResult",
    "compute_cloud_mask",
    "compute_joint_cloud_mask",
    "CloudMaskResult",
    "compute_spectral_indices",
    "SpectralIndices",
    "detect_surface_changes",
    "ChangeClassificationResult",
    "CLASS_UNCHANGED",
    "CLASS_NEW_BUILTUP",
    "CLASS_VEG_INCREASE",
    "CLASS_VEG_DECREASE",
    "CLASS_WATER_INCREASE",
    "CLASS_WATER_DECREASE",
    "CLASS_CLOUD_INVALID",
    "render_evidence_overlay",
    "RenderResult",
    "COLOR_PALETTE",
    "compute_change_statistics",
    "ChangeStatistics",
    "calculate_physical_area_statistics",
    "AreaMetricResult",
    "compute_pixel_area_hectares",
    "calculate_quality_score",
    "QualityAssessmentResult",
    "validate_analysis_input"
]
