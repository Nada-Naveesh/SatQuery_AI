"""
SatQuery AI - Remote Sensing Spectral Indices Engine
Computes NDVI (Vegetation), NDWI (Water), and NDBI / Built-up indicator from Sentinel-2 Level-2A reflectance bands.
"""

from typing import Optional
from dataclasses import dataclass
import numpy as np

from backend.app.processing.raster_loader import RasterScene


@dataclass
class SpectralIndices:
    """Calculated remote sensing spectral index maps for a single satellite scene."""
    ndvi: np.ndarray        # Normalized Difference Vegetation Index [-1.0, 1.0]
    ndwi: np.ndarray        # Normalized Difference Water Index [-1.0, 1.0]
    builtup_index: np.ndarray  # Built-up / Impervious Surface Indicator [-1.0, 1.0]
    brightness: np.ndarray  # Mean visible brightness [0.0, 1.0]
    has_true_nir: bool
    has_true_swir: bool


def compute_spectral_indices(scene: RasterScene) -> SpectralIndices:
    """
    Computes standard physical spectral indices from the scene's surface reflectance bands.
    
    Formulas:
      NDVI = (B08 - B04) / (B08 + B04 + eps)   [Vegetation Density & Health]
      NDWI = (B03 - B08) / (B03 + B08 + eps)   [Surface Water & Moisture, McFeeters 1996]
      NDBI = (B11 - B08) / (B11 + B08 + eps)   [Built-up & Impervious Infrastructure, Zha 2003]
    """
    r = scene.red.astype(np.float32)
    g = scene.green.astype(np.float32)
    b = scene.blue.astype(np.float32)
    brightness = (r + g + b) / 3.0
    eps = 1e-5

    has_true_nir = scene.nir is not None
    has_true_swir = scene.swir is not None

    if has_true_nir:
        nir = scene.nir.astype(np.float32)
        # 1. NDVI (Sentinel-2 B08 NIR & B04 Red)
        ndvi = (nir - r) / (nir + r + eps)

        # 2. NDWI (Sentinel-2 B03 Green & B08 NIR)
        # Water reflects green and strongly absorbs NIR, yielding positive values over water.
        ndwi = (g - nir) / (g + nir + eps)

        # 3. NDBI (Sentinel-2 B11 SWIR & B08 NIR) or Built-up Indicator
        if has_true_swir:
            swir = scene.swir.astype(np.float32)
            ndbi = (swir - nir) / (swir + nir + eps)
        else:
            # Built-up proxy combining Red/NIR difference and surface brightness
            # Impervious materials have higher Red reflectance than NIR compared to vegetation.
            red_nir_diff = (r - nir) / (r + nir + eps)
            ndbi = 0.65 * red_nir_diff + 0.35 * (brightness - 0.25)
    else:
        # Fallback for 3-band visible RGB imagery (proxy indices)
        # 1. Vegetation Index: Visible Atmospherically Resistant Index (VARI proxy)
        # Vegetation has strong green reflectance and red chlorophyll absorption.
        ndvi = (g - r) / (g + r + eps)

        # 2. Water Index: Blue-Red Water Ratio proxy
        # Water absorbs red wavelengths strongly, while vegetation reflects green >> blue and green >> red.
        # Water is dark (brightness < 0.38) and exhibits blue/cyan dominance without the vegetation green peak.
        is_water_candidate = (brightness < 0.38) & (b > r * 0.90) & (g < b * 1.25)
        raw_ndwi = (b - r) / (b + r + eps)
        ndwi = np.where(is_water_candidate, raw_ndwi, -0.6)

        # 3. Built-up / Impervious Surface Index:
        # Paved roads, concrete roofs, and engineered structures exhibit moderate-to-high brightness
        # and a flat, spectrally neutral response across visible bands (|r-g| < 0.08 and |g-b| < 0.08).
        is_urban_candidate = (brightness > 0.30) & (ndvi < 0.06)
        neutral_factor = 1.0 - np.clip(np.abs(r - g) + np.abs(g - b), 0.0, 1.0)
        ndbi = np.where(is_urban_candidate, (brightness - 0.28) * 2.0 * neutral_factor, -0.6)

    # Clip indices strictly to [-1.0, 1.0]
    ndvi = np.clip(ndvi, -1.0, 1.0)
    ndwi = np.clip(ndwi, -1.0, 1.0)
    builtup_index = np.clip(ndbi, -1.0, 1.0)

    return SpectralIndices(
        ndvi=ndvi,
        ndwi=ndwi,
        builtup_index=builtup_index,
        brightness=brightness,
        has_true_nir=has_true_nir,
        has_true_swir=has_true_swir
    )
