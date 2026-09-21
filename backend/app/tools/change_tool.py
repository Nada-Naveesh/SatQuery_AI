import time
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image

from backend.app.tools.base_tool import BaseSpecialistTool, ToolResult
from backend.app.processing import (
    load_raster_scene,
    align_scenes,
    compute_joint_cloud_mask,
    compute_spectral_indices,
    detect_surface_changes,
    render_evidence_overlay,
    compute_change_statistics
)


class BiTemporalChangeTool(BaseSpecialistTool):
    """
    Bi-Temporal Remote Sensing Change Analysis & CDVQA Specialist.
    Calculates surface transitions, urban expansion, vegetation shifts,
    and water boundary changes using physical spectral indices (NDVI, NDWI, NDBI).
    """
    @property
    def name(self) -> str:
        return "Siamese_Change_Specialist_v1"

    @property
    def task_type(self) -> str:
        return "change_detection"

    @property
    def model_checkpoint(self) -> str:
        return "changeformer-cdvqa-siamese-base"

    def run(
        self,
        images: List[np.ndarray],
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        start_t = time.perf_counter()
        if len(images) < 2:
            raise ValueError("Bi-Temporal Change Analysis requires at least 2 co-registered images (T1 and T2).")

        img1 = images[0]
        img2 = images[1]
        params = parameters or {}
        q = (query or "").lower().strip()

        # 1. Load standardized raster scenes
        scene1 = load_raster_scene(img1, filename=params.get("filename1", "t1.tif"))
        scene2 = load_raster_scene(img2, filename=params.get("filename2", "t2.tif"))

        # 2. Align spatial grid
        aligned = align_scenes(scene1, scene2)

        # 3. Compute joint atmospheric & cloud mask
        cloud_res = compute_joint_cloud_mask(aligned.scene1, aligned.scene2)

        # 4. Compute spectral indices (NDVI, NDWI, NDBI)
        indices1 = compute_spectral_indices(aligned.scene1)
        indices2 = compute_spectral_indices(aligned.scene2)

        # 5. Detect surface changes with MMU filtering
        change_result = detect_surface_changes(
            aligned.scene1,
            aligned.scene2,
            indices1,
            indices2,
            valid_mask=cloud_res.valid_mask
        )

        # 6. Compute ground-truth hectare statistics & quality-aware confidence
        date1 = params.get("date1") or params.get("date_t1") or "2025"
        date2 = params.get("date2") or params.get("date_t2") or "2026"
        loc_name = params.get("location_name") or params.get("area") or "this monitored area"

        stats = compute_change_statistics(
            change_result,
            resolution_m=aligned.scene2.resolution_m or 10.0,
            registration_quality=aligned.registration_quality,
            overlap_percentage=aligned.overlap_percentage,
            date_labels=(date1, date2),
            location_name=loc_name
        )

        # 7. Render authentic multi-color evidence overlay
        rendered = render_evidence_overlay(
            aligned.scene2.true_color,
            change_result,
            alpha=0.65,
            add_decorations=True,
            date_labels=(date1, date2),
            resolution_m=aligned.scene2.resolution_m or 10.0
        )

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        builtup_ha = stats.classes.get("new_builtup_ha", 0.0)
        veg_inc_ha = stats.classes.get("vegetation_increase_ha", 0.0)
        veg_dec_ha = stats.classes.get("vegetation_decrease_ha", 0.0)
        water_inc_ha = stats.classes.get("water_increase_ha", 0.0)
        water_dec_ha = stats.classes.get("water_decrease_ha", 0.0)

        # Query-specific natural language answering
        if any(w in q for w in ["built", "building", "urban", "construction", "road", "paved", "infrastructure"]):
            if builtup_ha > 0:
                lead_answer = f"Yes, new built-up and paved infrastructure increased by approximately {builtup_ha:.1f} hectares between {date1} and {date2} (highlighted in red)."
            else:
                lead_answer = f"No significant new built-up construction was detected in this area between {date1} and {date2}."
        elif any(w in q for w in ["flood", "water", "submerge", "river", "lake", "inundat"]):
            if water_inc_ha > 0:
                lead_answer = f"Yes, surface water and inundation expanded by about {water_inc_ha:.1f} hectares between {date1} and {date2} (highlighted in blue)."
            elif water_dec_ha > 0:
                lead_answer = f"Water levels receded by approximately {water_dec_ha:.1f} hectares between {date1} and {date2} (highlighted in purple)."
            else:
                lead_answer = f"Water bodies remained stable with no major flood inundation between {date1} and {date2}."
        elif any(w in q for w in ["tree", "forest", "green", "crop", "vegetation", "farm", "deforest"]):
            if veg_dec_ha > 0:
                lead_answer = f"Vegetation canopy decline / crop clearing affected about {veg_dec_ha:.1f} hectares (highlighted in yellow)."
            elif veg_inc_ha > 0:
                lead_answer = f"Vegetation growth / greening was observed across about {veg_inc_ha:.1f} hectares (highlighted in green)."
            else:
                lead_answer = f"Vegetation coverage remained stable across the monitored area between {date1} and {date2}."
        else:
            lead_answer = stats.simple_explanation

        # Compose full text answer
        text_ans = (
            f"{lead_answer}\n\n"
            f"Overall, {stats.changed_area_ha:.1f} hectares ({stats.changed_percentage:.1f}% of the {stats.area_of_interest_ha:.1f} ha monitored area) "
            f"experienced visible surface changes between {date1} and {date2}. "
            f"The evidence overlay highlights changes by type: red for new buildings and paved roads, "
            f"green for vegetation growth, yellow for vegetation loss, blue for water increase, and purple for water decrease. "
            f"Atmospheric quality indicates {stats.quality['valid_pixel_percentage']}% cloud-free visibility ({stats.confidence_label}, {stats.confidence_score*100:.1f}% confidence)."
        )

        bullets = [
            f"Total surface area changed: {stats.changed_area_ha:.1f} hectares ({stats.changed_percentage:.1f}% of monitored AOI).",
            f"New built-up & infrastructure: {builtup_ha:.1f} ha (highlighted in red).",
            f"Vegetation canopy loss / clearing: {veg_dec_ha:.1f} ha (highlighted in yellow).",
            f"Vegetation growth / greening: {veg_inc_ha:.1f} ha (highlighted in green).",
            f"Water surface expansion: {water_inc_ha:.1f} ha (blue); Water surface decline: {water_dec_ha:.1f} ha (purple).",
            f"Data Quality: {stats.quality['valid_pixel_percentage']}% clear optical pixels ({stats.confidence_label}, {stats.confidence_score*100:.1f}% score)."
        ]

        metric_summary = {
            "pixel_count": int(np.sum(change_result.classified_mask != 0)),
            "area_hectares": stats.changed_area_ha,
            "valid_area_hectares": stats.valid_area_ha,
            "total_area_hectares": stats.area_of_interest_ha,
            "coverage_pct": stats.changed_percentage,
            "builtup_expansion_hectares": builtup_ha,
            "vegetation_loss_hectares": veg_dec_ha,
            "vegetation_growth_hectares": veg_inc_ha,
            "water_increase_hectares": water_inc_ha,
            "water_decrease_hectares": water_dec_ha,
            "quality": stats.quality,
            "confidence_score": stats.confidence_score,
            "confidence_label": stats.confidence_label,
            "rgba_overlay_b64": rendered.rgba_base64,
            "explainable_legend": {
                "red": "New Built-up & Paved Roads",
                "green": "Vegetation / Canopy Growth",
                "yellow": "Vegetation Loss / Clearing",
                "blue": "Water Surface / Inundation",
                "purple": "Water Body Decline / Drying"
            }
        }

        return ToolResult(
            tool_name=self.name,
            task_type=self.task_type,
            text_output=text_ans,
            visual_overlay_b64=rendered.overlay_base64,
            visual_overlay_type="change_heatmap",
            confidence=stats.confidence_score,
            execution_time_ms=round(elapsed_ms, 2),
            parameters={
                "processing_engine": "SatQuery_Raster_Pipeline_v2",
                "resolution_m": stats.quality.get("ground_sample_distance_m", 10.0),
                "registration_quality": stats.quality.get("registration_quality", "good"),
                "overlap_pct": stats.quality.get("overlap_percentage", 100.0),
                "valid_pixel_pct": stats.quality.get("valid_pixel_percentage", 100.0),
                "date_t1": date1,
                "date_t2": date2,
                "location": loc_name
            },
            metric_summary=metric_summary,
            summary_bullet_points=bullets
        )
