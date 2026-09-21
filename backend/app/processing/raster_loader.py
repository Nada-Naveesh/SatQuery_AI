"""
SatQuery AI - Geospatial Raster Loader
Loads multi-band Sentinel-2 Level-2A GeoTIFFs, PNGs, and NumPy arrays into standardized reflectance tensors.
"""

import io
from pathlib import Path
from typing import Union, List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import numpy as np
from PIL import Image

try:
    import tifffile
    HAS_TIFFFILE = True
except ImportError:
    HAS_TIFFFILE = False


@dataclass
class RasterScene:
    """Standardized representation of a remote sensing scene."""
    data: np.ndarray  # float32 normalized reflectance [0.0, 1.0], shape (H, W, C)
    channels: List[str]
    height: int
    width: int
    num_channels: int
    resolution_m: float
    crs: str
    bbox: Optional[List[float]]
    true_color: np.ndarray  # uint8 RGB composite [0, 255], shape (H, W, 3)
    
    @property
    def blue(self) -> np.ndarray:
        if "B02" in self.channels:
            return self.data[:, :, self.channels.index("B02")]
        elif "Blue" in self.channels:
            return self.data[:, :, self.channels.index("Blue")]
        return self.data[:, :, 2] if self.num_channels >= 3 else self.data[:, :, 0]

    @property
    def green(self) -> np.ndarray:
        if "B03" in self.channels:
            return self.data[:, :, self.channels.index("B03")]
        elif "Green" in self.channels:
            return self.data[:, :, self.channels.index("Green")]
        return self.data[:, :, 1] if self.num_channels >= 2 else self.data[:, :, 0]

    @property
    def red(self) -> np.ndarray:
        if "B04" in self.channels:
            return self.data[:, :, self.channels.index("B04")]
        elif "Red" in self.channels:
            return self.data[:, :, self.channels.index("Red")]
        return self.data[:, :, 0]

    @property
    def nir(self) -> Optional[np.ndarray]:
        if "B08" in self.channels:
            return self.data[:, :, self.channels.index("B08")]
        elif "NIR" in self.channels:
            return self.data[:, :, self.channels.index("NIR")]
        elif self.num_channels >= 4:
            return self.data[:, :, 3]
        return None

    @property
    def swir(self) -> Optional[np.ndarray]:
        if "B11" in self.channels:
            return self.data[:, :, self.channels.index("B11")]
        elif "SWIR" in self.channels:
            return self.data[:, :, self.channels.index("SWIR")]
        return None


def _percentile_stretch(arr: np.ndarray, p_low: float = 2.0, p_high: float = 98.0) -> np.ndarray:
    """Stretches float band to [0, 1] using percentile clipping to preserve natural contrast."""
    val_low, val_high = np.percentile(arr, (p_low, p_high))
    if val_high > val_low:
        stretched = np.clip((arr - val_low) / (val_high - val_low), 0.0, 1.0)
    else:
        stretched = np.zeros_like(arr)
    return stretched


def load_raster_scene(
    source: Union[str, Path, bytes, np.ndarray],
    filename: str = "",
    bbox: Optional[List[float]] = None,
    resolution_m: float = 10.0,
    crs: str = "EPSG:4326"
) -> RasterScene:
    """
    Loads and normalizes a satellite scene from filesystem path, raw bytes, or existing numpy array.
    """
    raw_array = None
    resolved_name = filename

    # 1. Read from Path or string
    if isinstance(source, (str, Path)):
        p = Path(source)
        resolved_name = resolved_name or p.name
        if not p.exists():
            raise FileNotFoundError(f"Satellite raster not found at: {p}")
        
        is_tiff = p.suffix.lower() in (".tif", ".tiff")
        if is_tiff and HAS_TIFFFILE:
            try:
                raw_array = tifffile.imread(str(p))
            except Exception:
                pass
        
        if raw_array is None:
            pil_img = Image.open(str(p))
            raw_array = np.array(pil_img)

    # 2. Read from bytes
    elif isinstance(source, bytes):
        is_tiff = (
            resolved_name.lower().endswith((".tif", ".tiff"))
            or source[:4] in (b"II*\x00", b"MM\x00*")
        )
        if is_tiff and HAS_TIFFFILE:
            try:
                raw_array = tifffile.imread(io.BytesIO(source))
            except Exception:
                pass
        if raw_array is None:
            pil_img = Image.open(io.BytesIO(source))
            raw_array = np.array(pil_img)

    # 3. Existing numpy array
    elif isinstance(source, np.ndarray):
        raw_array = source.copy()
    else:
        raise ValueError(f"Unsupported raster source type: {type(source)}")

    # Ensure 3D shape (H, W, C)
    if raw_array.ndim == 2:
        raw_array = raw_array[:, :, np.newaxis]
    elif raw_array.ndim >= 3 and raw_array.shape[0] in (1, 2, 3, 4, 8, 12) and raw_array.shape[0] < raw_array.shape[1]:
        # Channel-first format (C, H, W) -> (H, W, C)
        raw_array = np.transpose(raw_array, (1, 2, 0))

    h, w, c = raw_array.shape

    # Normalize to float32 [0.0, 1.0]
    if raw_array.dtype == np.uint8:
        norm_data = raw_array.astype(np.float32) / 255.0
    elif raw_array.dtype in (np.uint16, np.int16):
        # Sentinel-2 Level-2A surface reflectance scaled by 10000
        norm_data = np.clip(raw_array.astype(np.float32) / 10000.0, 0.0, 1.0)
    else:
        norm_data = raw_array.astype(np.float32)
        if norm_data.max() > 1.0:
            norm_data = norm_data / max(norm_data.max(), 255.0)

    # Channel identification and true-color generation
    if c == 4:
        # Standard Sentinel-2 10m L2A package: B02 (Blue), B03 (Green), B04 (Red), B08 (NIR)
        channels = ["B02", "B03", "B04", "B08"]
        r_band = norm_data[:, :, 2]
        g_band = norm_data[:, :, 1]
        b_band = norm_data[:, :, 0]
    elif c >= 3:
        # Standard RGB (Red, Green, Blue)
        channels = ["Red", "Green", "Blue"] + [f"Band_{i}" for i in range(3, c)]
        r_band = norm_data[:, :, 0]
        g_band = norm_data[:, :, 1]
        b_band = norm_data[:, :, 2]
    elif c == 1:
        channels = ["Panchromatic"]
        r_band = g_band = b_band = norm_data[:, :, 0]
    else:
        channels = [f"Band_{i}" for i in range(c)]
        r_band = norm_data[:, :, 0]
        g_band = norm_data[:, :, 1 if c > 1 else 0]
        b_band = norm_data[:, :, 0]

    # Generate enhanced true-color composite [0, 255] uint8
    r_disp = (_percentile_stretch(r_band) * 255.0).astype(np.uint8)
    g_disp = (_percentile_stretch(g_band) * 255.0).astype(np.uint8)
    b_disp = (_percentile_stretch(b_band) * 255.0).astype(np.uint8)
    true_color = np.stack([r_disp, g_disp, b_disp], axis=2)

    return RasterScene(
        data=norm_data,
        channels=channels,
        height=h,
        width=w,
        num_channels=c,
        resolution_m=resolution_m,
        crs=crs,
        bbox=bbox,
        true_color=true_color
    )
