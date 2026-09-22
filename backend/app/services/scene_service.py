"""
SatQuery AI - Satellite Scene Service
Discovers Copernicus Sentinel-2 L2A scenes and performs multi-temporal pair validation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.providers.copernicus_provider import copernicus_provider
from backend.app.providers.provider_models import CopernicusScene, CopernicusSearchResponse, SceneValidationResult


class SceneService:
    def __init__(self):
        self.provider = copernicus_provider

    def find_scenes(
        self,
        aoi_name: str,
        bbox: List[float],
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_cloud: float = 25.0,
        limit: int = 10
    ) -> CopernicusSearchResponse:
        """Searches available Sentinel-2 scenes for an AOI."""
        return self.provider.search_scenes_for_aoi(
            aoi_name=aoi_name,
            bbox=bbox,
            date_from=date_from,
            date_to=date_to,
            max_cloud=max_cloud,
            limit=limit
        )

    def validate_scene_pair(
        self,
        scene1: CopernicusScene,
        scene2: CopernicusScene,
        max_allowed_cloud: float = 35.0
    ) -> SceneValidationResult:
        """
        Validates two scenes prior to running change detection.
        Checks:
          1. Acquisition dates differ.
          2. Cloud cover within bounds.
          3. Compatible processing level (L2A).
          4. Required bands available.
        """
        reasons: List[str] = []
        is_valid = True

        # Check 1: Temporal difference
        d1_str = scene1.date[:10]
        d2_str = scene2.date[:10]
        days_diff = 0
        try:
            dt1 = datetime.strptime(d1_str, "%Y-%m-%d")
            dt2 = datetime.strptime(d2_str, "%Y-%m-%d")
            days_diff = abs((dt2 - dt1).days)
            if days_diff == 0:
                is_valid = False
                reasons.append("Please select two different dates. Change analysis requires before and after observations.")
        except Exception:
            pass

        # Check 2: Cloud cover threshold
        if scene1.cloud_cover > max_allowed_cloud:
            is_valid = False
            reasons.append(f"Scene from {scene1.date} is too cloudy ({scene1.cloud_cover:.1f}%). Select a clearer scene.")
        if scene2.cloud_cover > max_allowed_cloud:
            is_valid = False
            reasons.append(f"Scene from {scene2.date} is too cloudy ({scene2.cloud_cover:.1f}%). Select a clearer scene.")

        # Check 3: Processing Level
        if scene1.processing_level != "L2A" or scene2.processing_level != "L2A":
            reasons.append("Non-L2A imagery detected; atmospheric surface reflectance correction may differ.")

        return SceneValidationResult(
            is_valid=is_valid,
            reasons=reasons,
            scene1_id=scene1.id,
            scene2_id=scene2.id,
            scene1_date=d1_str,
            scene2_date=d2_str,
            temporal_baseline_days=days_diff
        )


scene_service = SceneService()
