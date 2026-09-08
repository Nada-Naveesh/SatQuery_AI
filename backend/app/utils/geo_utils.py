from typing import Dict, Any, Tuple
import numpy as np

def estimate_spatial_metrics(mask: np.ndarray, gsd_meters: float = 10.0) -> Dict[str, Any]:
    """
    Calculates real-world spatial area metrics from a binary mask given Ground Sampling Distance.
    Default GSD is 10.0m (Sentinel-2 visual bands).
    """
    if mask.max() > 1.0:
        binary_mask = (mask > 127).astype(np.uint8)
    else:
        binary_mask = (mask > 0.5).astype(np.uint8)
        
    pixel_count = int(np.sum(binary_mask))
    total_pixels = binary_mask.size
    
    # Area per pixel in square meters
    pixel_area_m2 = gsd_meters * gsd_meters
    total_area_m2 = pixel_count * pixel_area_m2
    hectares = total_area_m2 / 10000.0
    percentage = (pixel_count / total_pixels) * 100.0 if total_pixels > 0 else 0.0
    
    return {
        "pixel_count": pixel_count,
        "total_pixels": total_pixels,
        "coverage_percentage": round(percentage, 2),
        "area_m2": round(total_area_m2, 2),
        "area_hectares": round(hectares, 2),
        "gsd_meters": gsd_meters
    }

def detect_modality_heuristics(filename: str, channels: int, arr: np.ndarray) -> str:
    """
    Detects whether an image is optical, multispectral, or SAR based on filename tags and channel statistics.
    """
    fn_lower = filename.lower()
    if any(k in fn_lower for k in ["sar", "s1", "risat", "vv", "vh", "radar"]):
        return "sar"
    if any(k in fn_lower for k in ["cartosat", "s2", "sentinel2", "optical", "rgb", "landsat"]):
        return "optical"
    if channels > 4:
        return "multispectral"
    
    # Check if image looks like single-band grayscale or SAR speckle
    if arr.ndim == 2 or (arr.ndim == 3 and np.allclose(arr[:, :, 0], arr[:, :, 1])):
        return "sar"
        
    return "optical"
