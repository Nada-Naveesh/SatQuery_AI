"""
SatQuery AI - Remote Sensing Change Detection & Surface Classification
Computes physical index differentials (ΔNDVI, ΔNDWI, ΔNDBI) and classifies surface transitions into
scientifically grounded semantic classes with morphological noise filtering.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

try:
    from scipy.ndimage import binary_opening, label
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from backend.app.processing.raster_loader import RasterScene
from backend.app.processing.indices import SpectralIndices


# Standardized Semantic Change Classes
CLASS_UNCHANGED = 0        # Transparent (No detected change)
CLASS_NEW_BUILTUP = 1      # Red (#ef4444)
CLASS_VEG_INCREASE = 2     # Green (#22c55e)
CLASS_VEG_DECREASE = 3     # Yellow/Orange (#eab308)
CLASS_WATER_INCREASE = 4   # Cyan/Blue (#06b6d4)
CLASS_WATER_DECREASE = 5   # Purple (#a855f7)
CLASS_CLOUD_INVALID = 255  # Dark Gray Hatch / Masked


@dataclass
class ChangeClassificationResult:
    """Classified change raster and individual semantic category masks."""
    classified_mask: np.ndarray  # uint8 array of CLASS_* IDs, shape (H, W)
    delta_ndvi: np.ndarray        # float32 ΔNDVI = NDVI_T2 - NDVI_T1
    delta_ndwi: np.ndarray        # float32 ΔNDWI = NDWI_T2 - NDWI_T1
    delta_builtup: np.ndarray     # float32 ΔBuiltup = NDBI_T2 - NDBI_T1
    spectral_diff: np.ndarray     # float32 L1 spectral distance
    builtup_mask: np.ndarray      # boolean 2D array
    veg_increase_mask: np.ndarray # boolean 2D array
    veg_decrease_mask: np.ndarray # boolean 2D array
    water_increase_mask: np.ndarray  # boolean 2D array
    water_decrease_mask: np.ndarray  # boolean 2D array
    cloud_mask: np.ndarray        # boolean 2D array (invalid pixels)


def _filter_small_noise(mask: np.ndarray, min_pixels: int = 9) -> np.ndarray:
    """Removes isolated speckle noise regions smaller than the minimum mapping unit."""
    if not HAS_SCIPY or min_pixels <= 1 or not np.any(mask):
        return mask

    # 3x3 structuring element for morphological opening
    struct = np.ones((3, 3), dtype=bool)
    cleaned = binary_opening(mask, structure=struct)
    
    # Also filter connected components strictly < min_pixels
    labeled, num_features = label(cleaned)
    if num_features > 0:
        counts = np.bincount(labeled.ravel())
        too_small = counts < min_pixels
        too_small[0] = False
        cleaned[too_small[labeled]] = False
    return cleaned


def detect_surface_changes(
    scene1: RasterScene,
    scene2: RasterScene,
    indices1: SpectralIndices,
    indices2: SpectralIndices,
    valid_mask: Optional[np.ndarray] = None,
    thresholds: Optional[Dict[str, float]] = None,
    min_mapping_unit_pixels: int = 9
) -> ChangeClassificationResult:
    """
    Executes categorized bi-temporal change detection based on spectral index deltas.
    Assigns every pixel to one of the standardized change classes or transparent unchanged.
    """
    h, w = scene2.height, scene2.width
    cfg = thresholds or {
        "builtup_increase": 0.15,
        "vegetation_increase": 0.16,
        "vegetation_decrease": -0.16,
        "water_increase": 0.16,
        "water_decrease": -0.16,
        "minimum_change": 0.08
    }

    # 1. Physical Index Differencing
    d_ndvi = indices2.ndvi - indices1.ndvi
    d_ndwi = indices2.ndwi - indices1.ndwi
    d_builtup = indices2.builtup_index - indices1.builtup_index

    # 2. Multi-spectral Euclidean difference
    c_limit = min(scene1.num_channels, scene2.num_channels)
    diff_spectral = np.abs(scene2.data[:, :, :c_limit] - scene1.data[:, :, :c_limit]).mean(axis=2)

    # 3. Validity mask (clear of clouds, shadows, and no-data borders)
    if valid_mask is None:
        valid_mask = np.ones((h, w), dtype=bool)
    invalid_mask = ~valid_mask

    # 4. Raw change candidate thresholding
    has_spectral_change = (diff_spectral > cfg.get("minimum_change", 0.08)) & valid_mask

    # Water increase / flood: strong positive NDWI delta + post-change scene is water (NDWI > 0.0)
    raw_water_inc = (d_ndwi > cfg.get("water_increase", 0.16)) & (indices2.ndwi > 0.0) & has_spectral_change
    # Water decrease / drying: strong negative NDWI delta + pre-change scene was water (NDWI > 0.0)
    raw_water_dec = (d_ndwi < cfg.get("water_decrease", -0.16)) & (indices1.ndwi > 0.0) & has_spectral_change & (~raw_water_inc)

    # Vegetation increase / crop growth: positive NDVI delta
    raw_veg_inc = (d_ndvi > cfg.get("vegetation_increase", 0.16)) & has_spectral_change & (~raw_water_inc)
    # Vegetation decrease / clearing: negative NDVI delta
    raw_veg_dec = (d_ndvi < cfg.get("vegetation_decrease", -0.16)) & has_spectral_change & (~raw_water_inc) & (~raw_water_dec)

    # New built-up / roads: positive built-up delta or combination of high spectral change + vegetation drop
    raw_builtup = (
        (d_builtup > cfg.get("builtup_increase", 0.15))
        | ((diff_spectral > 0.18) & (d_ndvi < -0.06) & (indices2.brightness > 0.25))
    ) & has_spectral_change & (~raw_water_inc) & (~raw_water_dec) & (~raw_veg_inc)

    # 5. Morphological Cleanup (Minimum Mapping Unit filtering)
    mmu = min_mapping_unit_pixels
    builtup_mask = _filter_small_noise(raw_builtup, mmu)
    veg_inc_mask = _filter_small_noise(raw_veg_inc, mmu)
    veg_dec_mask = _filter_small_noise(raw_veg_dec, mmu)
    water_inc_mask = _filter_small_noise(raw_water_inc, mmu)
    water_dec_mask = _filter_small_noise(raw_water_dec, mmu)

    # If an area has subtle spectral shifts not captured by the strict indices, preserve if noticeable
    # Ensure mutually exclusive semantic class assignment in prioritized order
    classified = np.zeros((h, w), dtype=np.uint8)
    classified[veg_dec_mask] = CLASS_VEG_DECREASE
    classified[veg_inc_mask] = CLASS_VEG_INCREASE
    classified[water_dec_mask] = CLASS_WATER_DECREASE
    classified[water_inc_mask] = CLASS_WATER_INCREASE
    classified[builtup_mask] = CLASS_NEW_BUILTUP
    classified[invalid_mask] = CLASS_CLOUD_INVALID

    return ChangeClassificationResult(
        classified_mask=classified,
        delta_ndvi=d_ndvi,
        delta_ndwi=d_ndwi,
        delta_builtup=d_builtup,
        spectral_diff=diff_spectral,
        builtup_mask=builtup_mask,
        veg_increase_mask=veg_inc_mask,
        veg_decrease_mask=veg_dec_mask,
        water_increase_mask=water_inc_mask,
        water_decrease_mask=water_dec_mask,
        cloud_mask=invalid_mask
    )
