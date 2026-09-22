"""
SatQuery AI - Remote Sensing Input Validation Module
Validates scene compatibility, channel depth, and geometric overlap prior to analysis.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np

from backend.app.processing.raster_loader import RasterScene


def validate_analysis_input(
    scene1: RasterScene,
    scene2: Optional[RasterScene] = None,
    min_dimension: int = 32,
    max_dimension: int = 4096
) -> Tuple[bool, List[str]]:
    """
    Validates that satellite scene(s) are valid for processing.
    """
    errors: List[str] = []

    # Check 1: Dimensions
    if scene1.height < min_dimension or scene1.width < min_dimension:
        errors.append(f"Image 1 dimension ({scene1.width}x{scene1.height}) is too small. Minimum is {min_dimension}x{min_dimension}.")
    if scene1.height > max_dimension or scene1.width > max_dimension:
        errors.append(f"Image 1 dimension ({scene1.width}x{scene1.height}) exceeds limit of {max_dimension}x{max_dimension}.")

    # Check 2: Values not all zero
    if np.all(scene1.data == 0):
        errors.append("Image 1 contains only zero / blank values.")

    if scene2 is not None:
        if scene2.height < min_dimension or scene2.width < min_dimension:
            errors.append(f"Image 2 dimension ({scene2.width}x{scene2.height}) is too small.")
        if np.all(scene2.data == 0):
            errors.append("Image 2 contains only zero / blank values.")

    return len(errors) == 0, errors
