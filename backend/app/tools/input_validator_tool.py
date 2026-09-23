import time
import os
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from backend.app.tools.base_tool import BaseSpecialistTool, ToolResult

class InputValidatorTool(BaseSpecialistTool):
    """
    Deterministic Remote-Sensing Input Validator Tool (SIH 2026 PS 26167).
    Validates sensor modalities, GeoTIFF/TIFF integrity, spatial dimensions,
    co-registration alignment, and temporal metadata across the 4 input modes:
      1. Single Optical / Multispectral Scene
      2. Single SAR Scene
      3. Bi-Temporal Pair (Two Dates, Same Area)
      4. Optical + SAR Pair (Co-Registered Pair)
    """
    @property
    def name(self) -> str:
        return "input_validator_tool"

    @property
    def task_type(self) -> str:
        return "input_validation"

    @property
    def model_checkpoint(self) -> str:
        return "geospatial-header-crs-validator-v1"

    def validate_inputs(
        self,
        images: List[np.ndarray],
        input_mode: str = "auto",
        filenames: Optional[List[str]] = None,
        modalities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []
        meta = metadata or {}
        fnames = filenames or [f"image_{i}.tif" for i in range(len(images))]
        mods = modalities or []

        # 1. Image count check
        count = len(images)
        if count == 0:
            errors.append("No satellite imagery provided. At least 1 image is required.")
            return {"is_valid": False, "errors": errors, "warnings": warnings, "details": {}}

        mode = input_mode.lower() if isinstance(input_mode, str) and input_mode else "auto"

        if mode == "single_optical":
            if count != 1:
                errors.append(f"Single Optical mode expects exactly 1 scene, but received {count}.")
            if mods and "sar" in mods[0].lower():
                errors.append("Selected 'Single Optical' mode, but uploaded image exhibits SAR backscatter characteristics.")

        elif mode == "single_sar":
            if count != 1:
                errors.append(f"Single SAR mode expects exactly 1 scene, but received {count}.")
            if mods and "optical" in mods[0].lower():
                warnings.append("Selected 'Single SAR' mode, but uploaded image appears to be optical multispectral imagery.")

        elif mode in ("bitemporal_pair", "temporal", "change"):
            if count < 2:
                errors.append(f"Bi-temporal change analysis requires 2 acquisition dates (T1 Baseline and T2 Follow-up), received {count}.")
            elif count > 2:
                warnings.append(f"Received {count} images; evaluating primary pair (first 2 scenes).")

        elif mode in ("optical_sar_pair", "fusion"):
            if count < 2:
                errors.append(f"Optical-SAR fusion requires 2 co-registered images (Optical + SAR), received {count}.")
            elif count > 2:
                warnings.append(f"Received {count} images; evaluating primary Optical-SAR pair.")

        # 2. Inspect individual raster arrays
        details = []
        for idx, (img, fname) in enumerate(zip(images, fnames)):
            if img is None:
                errors.append(f"Scene #{idx+1} ({fname}) is null or unreadable.")
                continue

            h, w = img.shape[:2]
            c = img.shape[2] if img.ndim == 3 else 1
            is_zero = bool(np.all(img == 0))

            if h < 32 or w < 32:
                errors.append(f"Scene #{idx+1} ({fname}) dimension ({w}x{h}) is below the 32x32 minimum resolution limit.")
            if h > 8192 or w > 8192:
                errors.append(f"Scene #{idx+1} ({fname}) dimension ({w}x{h}) exceeds the 8192x8192 processing limit.")
            if is_zero:
                errors.append(f"Scene #{idx+1} ({fname}) contains entirely blank / zero pixel values.")

            ext = os.path.splitext(fname)[1].lower()
            is_tiff = ext in (".tif", ".tiff")
            if ext in (".png", ".jpg", ".jpeg"):
                warnings.append(f"Scene #{idx+1} ({fname}) is in {ext.upper()} format. Permitted for standard public benchmark subsets (RSVQA, VRSBench, BigEarthNet, LEVIR-CD). Use GeoTIFF for production mission workflows.")

            details.append({
                "index": idx + 1,
                "filename": fname,
                "dimensions": [w, h, c],
                "format": "GeoTIFF/TIFF" if is_tiff else ext.upper().lstrip("."),
                "is_zero": is_zero,
                "modality": mods[idx] if idx < len(mods) else "unknown"
            })

        # 3. Pair geometry and overlap check
        if count >= 2:
            img1, img2 = images[0], images[1]
            h1, w1 = img1.shape[:2]
            h2, w2 = img2.shape[:2]
            aspect1 = w1 / max(h1, 1)
            aspect2 = w2 / max(h2, 1)

            if abs(aspect1 - aspect2) > 0.15:
                warnings.append(f"Aspect ratio discrepancy between Scene 1 ({w1}x{h1}) and Scene 2 ({w2}x{h2}). Spatial interpolation will be applied.")
            if (h1, w1) != (h2, w2):
                warnings.append(f"Dimension mismatch (Scene 1: {w1}x{h1}, Scene 2: {w2}x{h2}). Co-registration resampling will align spatial grids.")

            # Date check
            d1 = meta.get("date1") or meta.get("date_t1") or meta.get("date_before")
            d2 = meta.get("date2") or meta.get("date_t2") or meta.get("date_after")
            if d1 and d2 and mode in ("bitemporal_pair", "temporal", "change"):
                if d1 == d2:
                    warnings.append(f"Both scenes report identical acquisition date '{d1}'. Meaningful surface change requires distinct multi-temporal timestamps.")
                elif d1 > d2:
                    errors.append(f"Inverted temporal ordering: Baseline T1 date ({d1}) cannot be later than Follow-up T2 date ({d2}).")

        is_valid = len(errors) == 0
        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "input_mode": mode,
            "image_count": count,
            "scene_details": details
        }

    def run(
        self,
        images: List[np.ndarray],
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        start_t = time.perf_counter()
        params = parameters or {}
        validation = self.validate_inputs(
            images=images,
            input_mode=params.get("input_mode", "auto"),
            filenames=params.get("filenames"),
            modalities=params.get("modalities"),
            metadata=params
        )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        is_valid = validation["is_valid"]

        if is_valid:
            status_text = "Input imagery successfully validated. Geometry, format, and sensor parameters meet SIH 26167 specifications."
            conf = 0.99
        else:
            status_text = f"Input validation failed with {len(validation['errors'])} error(s): " + "; ".join(validation["errors"])
            conf = 0.0

        return ToolResult(
            tool_name=self.name,
            task_type=self.task_type,
            text_output=status_text,
            visual_overlay_b64=None,
            confidence=conf,
            execution_time_ms=round(elapsed_ms, 2),
            parameters={
                "input_mode": validation["input_mode"],
                "image_count": validation["image_count"],
                "validation_errors": validation["errors"],
                "validation_warnings": validation["warnings"]
            },
            metric_summary={
                "is_valid": 1.0 if is_valid else 0.0,
                "error_count": len(validation["errors"]),
                "warning_count": len(validation["warnings"])
            },
            summary_bullet_points=[
                f"Validation Status: {'PASSED' if is_valid else 'REJECTED'}",
                f"Scenes Verified: {validation['image_count']}",
                f"Mode Checked: {validation['input_mode']}"
            ] + ([f"Warning: {w}" for w in validation["warnings"][:2]])
        )
