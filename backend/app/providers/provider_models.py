"""
SatQuery AI - Copernicus & Remote Sensing Provider Data Models
Pydantic schemas for STAC discovery, scene metadata, and validation checks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CopernicusScene(BaseModel):
    id: str = Field(..., description="Unique Sentinel-2 product/scene identifier")
    date: str = Field(..., description="Acquisition date in YYYY-MM-DD format")
    cloud_cover: float = Field(..., description="Cloud cover percentage (0-100)")
    platform: str = Field(default="Sentinel-2", description="Satellite platform (e.g. Sentinel-2A/B)")
    processing_level: str = Field(default="L2A", description="Processing level, e.g. L2A Bottom-Of-Atmosphere")
    footprint: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON geometry of the scene footprint")
    quicklook_url: str = Field(..., description="URL or local path to scene preview/quicklook")
    available_bands: List[str] = Field(
        default_factory=lambda: ["B02", "B03", "B04", "B08", "B11", "SCL"],
        description="List of available spectral bands"
    )
    valid_for_comparison: bool = Field(default=True, description="Whether scene passes quality checks")
    warnings: List[str] = Field(default_factory=list, description="Quality warnings if any")
    coordinates_display: Optional[str] = None
    bbox_display: Optional[str] = None
    bbox: Optional[List[float]] = None
    resolution_m: float = 10.0


class CopernicusSearchResponse(BaseModel):
    provider: str = "Copernicus Data Space Ecosystem"
    collection: str = "Sentinel-2 Level-2A"
    aoi: str
    bbox: List[float]
    latitude: float
    longitude: float
    coordinates_display: str
    bbox_display: str
    count: int
    scenes: List[CopernicusScene]
    is_live_query: bool = False


class SceneValidationResult(BaseModel):
    is_valid: bool
    reasons: List[str] = Field(default_factory=list)
    scene1_id: str
    scene2_id: str
    scene1_date: str
    scene2_date: str
    temporal_baseline_days: int
